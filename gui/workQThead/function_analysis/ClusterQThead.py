from PyQt5.QtCore import QThread, pyqtSignal
import time

from config.global_config import software_name
from config.picture_config import normal_figsize_size
from service.FileService import readFile
from service.difference_analysis.MissingService import filter_by_ratio_no_group
from service.picture.basic import draw_line_chart, draw_heatmap
from util.Logger import logger
import util.Global as gol
import os
import datetime
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.cluster import KMeans
from yellowbrick.cluster.elbow import kelbow_visualizer
import matplotlib.pyplot as plt
import pandas as pd
from service.picture.show_data_cluster import draw_pca_cluster
from service.picture.show_dynamic_html import pca_plot_html
from service.difference_analysis.MissingService import filter
import numpy as np


plt.rc('font',family='Times New Roman')

class ClusterQThread(QThread):
    # 失败时传出信号
    error_trigger = pyqtSignal(str)
    # 正常运行过程中的日志输出
    info_trigger = pyqtSignal(str, str)

    def __int__(self):
        super(ClusterQThread, self).__init__()

    def over(self, start_time, if_sucess):
        '''
        结束时执行的操作
        '''
        end_time = time.time()
        if if_sucess:
            text = "数据分析运行成功,"
        else:
            text = "数据分析运行失败,"
        self.info_trigger.emit(text, "总时长为：" + str(end_time - start_time) + " s")

    def info_record(self, step, text):
        self.info_trigger.emit(step, text)

    def run(self):
        try:
            self._run()
        except Exception as e:
            # 日志记录
            logger.exception("Exception Logged")
            # self.exc_traceback = ''.join(traceback.format_exception(*sys.exc_info()))
            msg = repr(e)
            if "Permission" in msg:
                if ".xlsx" in str(e):
                    msg = "生成的excel结果文件已经打开，请先关闭excel文件"
                elif ".pdf" in str(e):
                    msg = "生成的PDF结果文件已经打开，请先关闭PDF文件"
                else:
                    msg = "生成的结果文件已经打开，请先关闭相应的文件"
            self.error_trigger.emit(msg)

    def _run(self):
        start_time = time.time()
        logger.debug("K-means富集分析开始")
        cluster_expression_path = gol.get_value("cluster_expression_path")
        cluster_result_path = gol.get_value("cluster_result_path")
        auto_cluster_class_num = gol.get_value("auto_cluster_class_num")
        cluster_class_num = gol.get_value("cluster_class_num")
        cluster_dim_index = gol.get_value("cluster_dim_index")
        if os.path.exists(cluster_expression_path) and os.path.exists(cluster_result_path):
            df = readFile(cluster_expression_path,index_col=None,if_zero_na=True)
            # 基因名称后面加上序号
            df.index = df.apply(lambda row: str(row[0]) + "_" + str(row.name), axis=1)
            df.index.name = df.iloc[:,0].name+"_No"
            df.drop(df.iloc[:,0].name, axis=1,inplace=True)
            # 一定要过滤掉缺失值过多的基因
            filter_df = filter_by_ratio_no_group(df, 0.5)
            filter_row_num = len(df) - len(filter_df)
            self.info_record("数据过滤", "根据缺失值比例大于50%的规则，一共过滤掉" + str(filter_row_num) + "行。")
            # 取log2
            if (not (filter_df < 0).values.any()) and (filter_df.max(skipna=True).max() >100):
                self.info_record("对数据取log2", "")
                filter_df = filter_df.applymap(lambda x: np.log2(x))
            # 用0值来填补缺失值
            filter_df.fillna(0,inplace=True)

            if cluster_dim_index==0:
                # 此时对样本聚类
                filter_df = filter_df.T # 转为行为样本，列为特征的表达矩阵

                # 取cv为前cluster_cv_ratio的基因进行聚类分析
                cluster_cv_ratio = gol.get_value("cluster_cv_ratio")

                cv = filter_df.std() / filter_df.mean() # 计算变异系数
                cv_sorted = cv.sort_values(ascending=False) # 按照变异系数从大到小排序
                n_features = int(len(cv) * (cluster_cv_ratio/100)) # 选取前20%的特征
                selected_features = cv_sorted.index[:n_features]
                self.info_record("选取前20%的基因", "一共有"+str(len(selected_features))+"个基因表达矩阵用于聚类分析")
                filter_df = filter_df.loc[:,selected_features]

            # 确定类的数目
            pdf_file_path = os.path.join(cluster_result_path, "cluster_k_means.pdf")
            pdf = PdfPages(pdf_file_path, metadata={'Creator': software_name, 'CreationDate': datetime.datetime.now(),
                                                    'Title': 'Cluster'})
            if auto_cluster_class_num or cluster_class_num is None:
                # 软件自动选择类的数目
                k = self.get_k(filter_df,pdf)
                self.info_record("软件自动确定聚类的数目为",str(k))
            else:
                k = int(cluster_class_num)
            result_df = self.k_means_fuc(filter_df,k,cluster_result_path)
            self.info_record("表格结果", "生成对应的excel文件")
            # 聚类结果可视化
            # 参考文章 https://blog.csdn.net/qazplm12_3/article/details/78904744
            class_nums = result_df['class_label'].nunique()
            groups_dict = {}
            groups = []
            for class_num in range(class_nums):
                groups_dict[str(class_num)]=result_df.loc[result_df["class_label"]==class_num].index.to_list()
                groups.append(groups_dict[str(class_num)])
            draw_pca_cluster(result_df[result_df.columns.difference(['class_label'])].transpose(),groups_dict,"K-means Cluster",pdf)

            PCA_raw_file_path = os.path.join(cluster_result_path, "PCA_cluster.html")
            pca_plot_html(result_df[result_df.columns.difference(['class_label'])].transpose(), PCA_raw_file_path, groups_dict, title="Raw")

            # 每个类别在每个样本中的表达平均值的log2的折线图
            class_mean_exp = result_df.pivot_table(index='class_label', aggfunc=np.mean)
            # class_mean_exp = np.log2(class_mean_exp) # 前面已经取了log2不再需要
            draw_line_chart(class_mean_exp,"Expression of different classes",pdf)

            draw_heatmap(result_df,"Expression heatmap of different classes",pdf,groups)


            pdf.close()
            self.info_record("结果可视化","生成PCA图、折线图、热图.")
            # 运行结束
            self.over(start_time, True)
        else:
            self.error_trigger.emit("导入的表达数据或结果文件夹不存在")
            self.over(start_time, False)
            return None

    def get_k(self,df,pdf):
        pdf.attach_note(
            "Use the 'elbow' method to select the optimal number of clusters for K-means clustering.",
            positionRect=[0, 0, 0, 0])
        plt.figure(figsize=normal_figsize_size)
        oz = kelbow_visualizer(KMeans(random_state=4), df, k=(2, 10), show=False)
        k = oz.elbow_value_
        pdf.savefig()
        plt.close()
        return k

    def k_means_fuc(self,df,k,cluster_result_path):
        k_means = KMeans(n_clusters=k, init='k-means++', random_state=0)
        k_means.fit(df)
        k_means_result = k_means.predict(df)

        # 输出文件
        columns = df.columns.values
        df["class_label"] = k_means_result
        cluster_centers = pd.DataFrame(k_means.cluster_centers_, columns=columns)
        xlsx_path = os.path.join(cluster_result_path, 'k_means_result.xlsx')
        with pd.ExcelWriter(xlsx_path) as writer:
            df.to_excel(writer, sheet_name='k-means-result')
            cluster_centers.to_excel(writer, sheet_name='k-means-cluster-centers')

        return df