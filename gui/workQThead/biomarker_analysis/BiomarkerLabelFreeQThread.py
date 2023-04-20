'''
无标记定量的蛋白质组学生物标志物筛选
'''
from PyQt5.QtCore import QThread, pyqtSignal
import time, os, datetime

from service.picture.show_data_cluster import draw_pca_cluster
from service.picture.show_dynamic_html import pca_plot_html
from util.Logger import logger
import util.Global as gol
from service.FileService import readFile
from service.biomarker_analysis.UtilService import create_result_dir, handle_test_data
from service.difference_analysis.UtilService import check_data_label_free_pro,extract_gene_name,get_groups_dict_list,export_data
from service.difference_analysis.DropConRevService import drop_CON_REV
from service.PdfService import ResultPdf
from service.difference_analysis.NormalizationService import upper_quantile_norm, quantile_norm, flatten_sum_norm, \
    FOT_norm
from service.difference_analysis.MissingService import filter_by_n, base_missing_filing, knn_missing_filter, \
    forest_missing_filing, filter_by_ratio
from service.difference_analysis.DifferenceAnalysisService import dfp_analysis
from service.difference_analysis.VisualizationService import data_imputation, data_norm, data_filter, data_dfp_analysis, \
    data_assesment
from service.biomarker_analysis.DatasetSplitService import tips,dataset_split
from service.biomarker_analysis.FeatureSelectService import feature_select, difference_analysis_plot, \
    feature_select_plot, get_final_features
from sklearn.preprocessing import StandardScaler
from matplotlib.backends.backend_pdf import PdfPages
from config.global_config import biomarker_preprocess_dirname,biomarker_data_split_dirname,biomarker_feature_select_dirname,biomarker_model_dirname
import pandas as pd
import numpy as np
from config.global_config import software_name
from service.biomarker_analysis.ModelBuildService import SGD_model, lr_model, random_forest_model, svm_model, \
    naive_bayes_model, get_best_model_name, model_in_test


class BiomarkerLabelFreeQThread(QThread):
    # 失败时传出信号
    error_trigger = pyqtSignal(str)
    # 正常运行过程中的日志输出
    info_trigger = pyqtSignal(str, str)

    def __int__(self):
        super(BiomarkerLabelFreeQThread, self).__init__()
        self.pdf = None
        self.i = 0

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
        # 创建pdf
        self.pdf.create()

    def info_record(self, step, text):
        self.info_trigger.emit(step, text)
        self.pdf.add_content(step, text)

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
            self.pdf.create()

    def difference_analysis_select(self,data,groups_dict,pgroup,result_path,complement_expression_df,p,if_p):
        # 差异蛋白分析
        fc_index = gol.get_value("biomarker_label_free_fc_index")
        if fc_index==0:
            fc = 1.5
        elif fc_index==1:
            fc=1.25
        elif fc_index ==2:
            fc = 2
        elif fc_index==3:
            fc = 3
        elif fc_index==4:
            fc=4
        else:
            raise Exception("差异倍数FC的范围取值异常")
        analysis = dfp_analysis(data, groups_dict, FC_threshold=fc, E_group=pgroup,p=float(p),if_p=if_p,already_log2=True)

        all = pd.merge(data, analysis, left_index=True, right_index=True)
        all["abs_log2FC"] = all["log2FC"].apply(lambda x:abs(x))
        ## 排序有问题
        all2 = pd.DataFrame()
        tmp_df1 = all[all["DEP"]!="none-significant"]
        tmp_df1.sort_values(by=["abs_log2FC"], ascending=[False], inplace=True)
        all2 = all2.append(tmp_df1)
        tmp_df2 = all[all["DEP"]=="none-significant"]
        all2 = all2.append(tmp_df2)
        dfp_len = len(tmp_df1)
        # all.sort_values(by = ["abs_log2FC",'Pvalue'],ascending=[False,True],inplace=True)
        # all2.drop(columns="abs_log2FC",inplace=True)
        export_data(all2, result_path, biomarker_feature_select_dirname,
                    "difference_analysis.xlsx", "difference analysis",complement_expression_df.loc[all.index, :])
        return all2,analysis,fc,dfp_len

    def feature_select_fuc(self,X_train,y_train,groups_dict,groups,simples,pgroup,result_path,complement_expression_df):
        feature_select_index = gol.get_value("biomarker_label_free_feature_select_index")
        feature_select_str = gol.get_value("biomarker_label_free_feature_select")
        # fc_despri = gol.get_value("biomarker_label_free_fc","")
        max_feature_num = gol.get_value("biomarker_label_free_max_feature_num")
        difference_analysis_data = pd.DataFrame(X_train.values.T, index=X_train.columns, columns=X_train.index)
        X_train_prepared = X_train

        file_path = os.path.join(result_path, biomarker_feature_select_dirname, "Show_Feature_Selection.pdf")
        dir_path = os.path.join(result_path, biomarker_feature_select_dirname)
        pdf = PdfPages(file_path, metadata={'Creator': software_name, 'CreationDate': datetime.datetime.now(),
                                            'Title': 'Feature Selection'})
        # P值
        pro_p_threshold_index = gol.get_value("biomarker_label_free_p_threshold_index")
        p = gol.get_value("biomarker_label_free_p")  # P值or FDR值
        if pro_p_threshold_index == 0:
            if_p = True
            pvalue_colname = "Pvalue"
        else:
            if_p = False
            pvalue_colname = "fdr"

        if feature_select_index in [0,1,2,3,4]:
            # 差异分析
            difference_analysis_df, analysis, fc, dfp_len = self.difference_analysis_select(difference_analysis_data,
                                                                                            groups_dict, pgroup,
                                                                                            result_path,
                                                                                            complement_expression_df,p,if_p)

            difference_analysis_plot(difference_analysis_df, fc, groups, simples, groups_dict, pdf, p_value=float(p),dir_path=dir_path,pvalue_colname=pvalue_colname)
            if feature_select_index!=0:
                deps = difference_analysis_df[difference_analysis_df["DEP"]!="none-significant"].index
                analysis = analysis[analysis["DEP"]!="none-significant"]
                X_train_prepared = X_train_prepared.loc[:,deps]
                logger.info(f"经过差异分析特征筛选后的训练集的shape:{X_train_prepared.shape}")

        if feature_select_index == 0:
            if dfp_len>max_feature_num:
                final_select_proteins = list(difference_analysis_df.index[0:max_feature_num])
            else:
                final_select_proteins = list(difference_analysis_df.index[0:dfp_len])
            final_select_proteins_import_df = difference_analysis_df.loc[final_select_proteins,"abs_log2FC"].to_frame()
            final_select_proteins_import_df.rename(columns={"abs_log2FC":"feature_importance"}, inplace=True)
        elif feature_select_index==1:
            # 差异基因+Lasso
            feature_select_result = feature_select(X_train_prepared,y_train,list(X_train_prepared.columns),max_feature_num,method="lasso")
            difference_analysis_model_df= pd.concat([feature_select_result, analysis], axis=1)
            export_data(difference_analysis_model_df, result_path, biomarker_feature_select_dirname,
                        "difference_analysis_Lasso_Feature_Selection.xlsx", "Feature_Selection",complement_expression_df.loc[difference_analysis_model_df.index, :])

            feature_select_plot(feature_select_result, difference_analysis_data, groups_dict, groups, pdf,dir_path=dir_path)
            final_select_proteins_import_df,final_select_proteins =get_final_features(difference_analysis_model_df, max_feature_num, "lasso")
            # export_data(final_select_proteins_import_df, result_path, biomarker_feature_select_dirname,
            #             "final_features.xlsx", "final_features")
            final_select_proteins_import_df.rename(columns={"lasso":"feature_importance"}, inplace=True)
        elif feature_select_index==2:
            # 差异分析 + 随机森林特征筛选
            feature_select_result = feature_select(X_train_prepared, y_train, list(X_train_prepared.columns), max_feature_num,
                                                   method="RF")
            difference_analysis_model_df = pd.concat([feature_select_result, analysis], axis=1)
            export_data(difference_analysis_model_df, result_path, biomarker_feature_select_dirname,
                        "difference_analysis_RandomForest_Feature_Selection.xlsx", "Feature_Selection",
                        complement_expression_df.loc[difference_analysis_model_df.index, :])
            feature_select_plot(feature_select_result, difference_analysis_data, groups_dict, groups, pdf,dir_path=dir_path)
            final_select_proteins_import_df, final_select_proteins = get_final_features(difference_analysis_model_df, max_feature_num,
                                                                          "RF")
            # export_data(final_select_proteins_import_df, result_path, biomarker_feature_select_dirname,
            #             "final_features.xlsx", "final_features")
            final_select_proteins_import_df.rename(columns={"RF": "feature_importance"}, inplace=True)
        elif feature_select_index==3:
            # 差异分析 + 递归特征消除法
            feature_select_result = feature_select(X_train_prepared, y_train, list(X_train_prepared.columns), max_feature_num,
                                                   method="RFE")
            difference_analysis_model_df = pd.concat([feature_select_result, analysis], axis=1)
            export_data(difference_analysis_model_df, result_path, biomarker_feature_select_dirname,
                        "difference_analysis_RFE_Feature_Selection.xlsx", "Feature_Selection",
                        complement_expression_df.loc[difference_analysis_model_df.index, :])
            feature_select_plot(feature_select_result, difference_analysis_data, groups_dict, groups, pdf,dir_path=dir_path)
            final_select_proteins_import_df, final_select_proteins = get_final_features(difference_analysis_model_df, max_feature_num,
                                                                          "RFE")
            # export_data(final_select_proteins_import_df, result_path, biomarker_feature_select_dirname,
            #             "final_features.xlsx", "final_features")
            final_select_proteins_import_df.rename(columns={"RFE": "feature_importance"}, inplace=True)
        elif feature_select_index==4:
            # 差异分析 + 岭回归特征筛选
            feature_select_result = feature_select(X_train_prepared, y_train, list(X_train_prepared.columns), max_feature_num,
                                                   method="l2")
            difference_analysis_model_df = pd.concat([feature_select_result, analysis], axis=1)
            export_data(difference_analysis_model_df, result_path, biomarker_feature_select_dirname,
                        "difference_analysis_L2_Feature_Selection.xlsx", "Feature_Selection",
                        complement_expression_df.loc[difference_analysis_model_df.index, :])
            feature_select_plot(feature_select_result, difference_analysis_data, groups_dict, groups, pdf,dir_path=dir_path)
            final_select_proteins_import_df, final_select_proteins = get_final_features(difference_analysis_model_df, max_feature_num,
                                                                          "l2")
            # export_data(final_select_proteins_import_df, result_path, biomarker_feature_select_dirname,
            #             "final_features.xlsx", "final_features")
            final_select_proteins_import_df.rename(columns={"l2": "feature_importance"}, inplace=True)
        # elif feature_select_index==5:
        #     feature_select_result = feature_select(X_train_prepared, y_train, list(X_train_prepared.columns), max_feature_num,
        #                                            method="lasso")
        #     export_data(feature_select_result, result_path, biomarker_feature_select_dirname,
        #                 "Lasso_Feature_Selection.xlsx", "Feature_Selection",
        #                 complement_expression_df.loc[feature_select_result.index, :])
        #
        #     feature_select_plot(feature_select_result, difference_analysis_data, groups_dict, groups, pdf,dir_path=dir_path)
        #     final_select_proteins_import_df, final_select_proteins = get_final_features(feature_select_result,
        #                                                                                 max_feature_num, "lasso")
        #     export_data(final_select_proteins_import_df, result_path, biomarker_feature_select_dirname,
        #                 "final_features.xlsx", "final_features")
        #     final_select_proteins_import_df.rename(columns={"lasso": "feature_importance"}, inplace=True)
        else:
            logger.error("您选择的特征筛选方法不正确")
            self.error_trigger.emit("您选择的特征筛选方法不正确")
            self.pdf.add_simple_content("您选择的特征筛选方法不正确")
            return None,None

        draw_pca_cluster(difference_analysis_data.loc[final_select_proteins, simples], groups_dict, "Final Select Proteins", pdf,dir_path=dir_path)

        PCA_file_path = os.path.join(result_path, biomarker_feature_select_dirname, "PCA_based_on_Final_Select_Proteins.html")
        pca_plot_html(difference_analysis_data.loc[final_select_proteins, simples], PCA_file_path, groups_dict, title="Final Select Proteins")

        pdf.close()
        # final_select_proteins = X_train.columns.to_list() # 不进行特征选择时
        self.info_record("特征筛选", "经过'"+feature_select_str+"'特征筛选，得到的特征为："+str(final_select_proteins)+",一共有"+str(len(final_select_proteins))+"个基因。")
        self.pdf.add_simple_content("注*：基因名称后面加上了'_XX'，数字代表基因在原始数据中的位置，从0开始数。")
        return final_select_proteins,final_select_proteins_import_df

    def _run(self):
        start_time = time.time()
        logger.debug("无标记定量蛋白质生物标志物分析开始")
        biomarker_label_free_expression_path = gol.get_value("biomarker_label_free_expression_path")
        biomarker_label_free_information_path = gol.get_value("biomarker_label_free_information_path")
        biomarker_label_free_result_path = gol.get_value("biomarker_label_free_result_path")
        if_gene_name = gol.get_value("biomarker_label_free_if_gene_name")
        if if_gene_name:
            gene_col_name = gol.get_value("biomarker_label_free_gene_name")
        else:
            gene_col_name = "Gene names"
        # pdf记录分析过程
        pdf_path = os.path.join(biomarker_label_free_result_path, "readme.pdf")
        self.pdf = ResultPdf(pdf_path, "无标记定量蛋白质组学数据生物标志物分析结果")

        # 创建结果文件夹
        create_result_dir(biomarker_label_free_result_path)

        expression_df = readFile(biomarker_label_free_expression_path, if_zero_na=True,index_col=None)
        information_df = readFile(biomarker_label_free_information_path,if_zero_na=False, index_col=None)
        # 检测数据是否符合要求
        result, despri = check_data_label_free_pro(expression_df, information_df)
        if not result:
            self.error_trigger.emit(despri)
            self.pdf.add_simple_content(despri)
            self.over(start_time, False)
            return None
        # 针对PD的数据，需要从 Description 列中提取 ”Gene names“
        expression_df = extract_gene_name(expression_df)
        if_applicable_newdata= True # 如果需要使用新的独立数据集做为测试集需要原始数据集种包含Gene names
        # 修改表达数据的行名与列名
        if gene_col_name in expression_df.columns:
            # expression_df[gene_col_name].fillna("", inplace=True)
            na_gene_num = expression_df[gene_col_name].isnull().sum()
            if na_gene_num>0:
                expression_df.dropna(axis=0, subset=[gene_col_name], inplace=True)
                self.info_record("删除基因名缺失的蛋白", "我们删除了"+str(na_gene_num)+"个基因名缺失('"+gene_col_name+"'列为空值)的蛋白.")
            expression_df.index = expression_df.apply(lambda row: str(row[gene_col_name]) + "_" + str(row.name), axis=1)
            expression_df.index.name = "Gene names_No."
        else:
            expression_df.index.name = "No."
            if_applicable_newdata=False
        logger.debug("删除污染与反库蛋白")
        # 删除污染与反库蛋白
        expression_df, despri = drop_CON_REV(expression_df)
        self.info_record("删除污染与反库蛋白", despri)
        # 更改列名
        logger.debug("更改列名")
        complement_expression_df = expression_df.drop(information_df["id"], axis=1)
        expression_df = expression_df.loc[:, information_df["id"]]
        expression_df.columns = information_df["name"]

        groups_dict, groups, simples = get_groups_dict_list(information_df)
        # 数据质量评估
        data_assesment(expression_df, biomarker_label_free_result_path, groups_dict,groups,simples,dirname="0-Data_Quality_Assessment")
        self.info_record("数据质量评估", "生成数据分布/数据缺失情况/样本相关性/样本聚类等图")
        # 校正
        norm_index = gol.get_value("biomarker_label_free_norm_index")
        if norm_index == 0:
            biomarker_label_free_norm = "upper quantile normalization"
            expression_norm_df = upper_quantile_norm(expression_df)
        elif norm_index == 1:
            biomarker_label_free_norm = "quantile normalization"
            expression_norm_df = quantile_norm(expression_df)
        elif norm_index ==3:
            biomarker_label_free_norm = "flatten sum normalization"
            expression_norm_df = flatten_sum_norm(expression_df)
        elif norm_index==4:
            biomarker_label_free_norm = "FOT normalization"
            expression_norm_df = FOT_norm(expression_df)
        else:
            biomarker_label_free_norm = "no normalization"
            expression_norm_df = expression_df
        self.info_record("数据校正", biomarker_label_free_norm + "-样本间（列）校正")
        data_norm(expression_df, expression_norm_df, biomarker_label_free_norm, biomarker_label_free_result_path,groups_dict,dirname=biomarker_preprocess_dirname)
        export_data(expression_norm_df, biomarker_label_free_result_path, biomarker_preprocess_dirname,
                    "normalization.xlsx", biomarker_label_free_norm)

        # 数据过滤
        filter_index = gol.get_value("biomarker_label_free_filter_index")
        if filter_index == 0:
            miss_n = gol.get_value("biomarker_label_free_miss_n")
            expression_filter_df = filter_by_n(expression_norm_df, miss_n, groups)
            filter_rule = f"各组中非缺失值数量低于{miss_n}过滤掉"
        elif filter_index == 1:
            miss_ratio = gol.get_value("biomarker_label_free_miss_ratio")
            if miss_ratio > 1:
                miss_ratio = float(miss_ratio / 100)
            expression_filter_df = filter_by_ratio(expression_norm_df, miss_ratio, groups)
            filter_rule = f"各组中缺失值比例高于{miss_ratio}%过滤掉"
        else:
            raise Exception("The selected missing value filtering rule is out of range")
        filter_row_num = len(expression_norm_df) - len(expression_filter_df)
        self.info_record("数据过滤", "分组过滤，" + filter_rule + "，一共过滤掉" + str(filter_row_num) + "行。")
        export_data(expression_filter_df, biomarker_label_free_result_path, biomarker_preprocess_dirname,
                    "normalization_and_filter.xlsx", "normalization_filter")
        data_filter(expression_norm_df, expression_filter_df, None, biomarker_label_free_result_path, groups_dict,dirname=biomarker_preprocess_dirname)

        # 缺失值填补
        imputation_index = gol.get_value("biomarker_label_free_imputation_index")
        if imputation_index == 0:
            biomarker_label_free_imputation = "minimum filling"
            expression_imputation_df = base_missing_filing(expression_filter_df,groups=groups)
        elif imputation_index == 1:
            biomarker_label_free_imputation = "KNN filling"
            expression_imputation_df = knn_missing_filter(expression_filter_df)
        else:
            biomarker_label_free_imputation = "random forest filling"
            expression_imputation_df = forest_missing_filing(expression_filter_df)
        self.info_record("缺失值填补", "填补方式："+biomarker_label_free_imputation)
        data_imputation(expression_filter_df, expression_imputation_df, biomarker_label_free_imputation, biomarker_label_free_result_path, groups_dict,biomarker_preprocess_dirname)
        export_data(expression_imputation_df, biomarker_label_free_result_path, biomarker_preprocess_dirname,
                    "normalization_filter_imputation.xlsx", "normalization_filter_imputation")
        ## 预处理基本步骤完成，接下来取log2
        if not (expression_imputation_df < 0).values.any():
            expression_imputation_df = expression_imputation_df.applymap(lambda x: np.log2(x))
        # 数据集拆分
        train_ratio = gol.get_value("biomarker_label_free_train_ratio")
        test_ratio = gol.get_value("biomarker_label_free_test_ratio")
        verification_ratio = gol.get_value("biomarker_label_free_verification_ratio")
        # 训练集用来对模型参数进行调整、验证集用来选出泛化较好的模型（参数），测试用来检验模型的泛化性能。
        self.info_record("数据集拆分", "训练集比例："+str(train_ratio)+"；验证集比例："+str(verification_ratio)+"；测试集比例："+str(test_ratio))
        tips_result,tips_despri = tips(groups,train_ratio,test_ratio,verification_ratio,"biomarker_label_free_test_data_path")
        if not tips_result:
            self.error_trigger.emit(tips_despri)
            self.pdf.add_simple_content(tips_despri)
            self.over(start_time, False)
            return None
        if tips_despri!="":
            self.pdf.add_simple_content(tips_despri)
            self.info_trigger.emit("样本数量存在的问题,这些问题会对生物标志物筛选产生影响", tips_despri)


        ngroup = gol.get_value("biomarker_label_free_ngroup") # 阴性
        pgroup = gol.get_value("biomarker_label_free_pgroup") # 阳性
        train_set,verification_set,test_set = dataset_split(expression_imputation_df, test_ratio,verification_ratio, train_ratio, ngroup, pgroup, groups_dict)
        export_data(train_set.T, biomarker_label_free_result_path, biomarker_data_split_dirname,
                    "train_set.xlsx", "train set")
        if test_set is not None:
            export_data(test_set.T, biomarker_label_free_result_path, biomarker_data_split_dirname,
                        "test_set.xlsx", "test set")
        if verification_set is not None:
            export_data(verification_set.T, biomarker_label_free_result_path, biomarker_data_split_dirname,
                        "valid_set.xlsx", "valid set")
        # 更新下groups_dict, groups, simples
        groups_dict, groups, simples = get_groups_dict_list(information_df[information_df["name"].isin(train_set.index)])

        # 特征筛选
        X_train = train_set.drop("class", axis=1)
        y_train = train_set["class"].copy()


        select_proteins, select_proteins_import_df = self.feature_select_fuc(X_train,y_train,groups_dict,groups,simples,pgroup,biomarker_label_free_result_path,complement_expression_df)
        if select_proteins is None or len(select_proteins)==0:
            self.over(start_time, False)
            return None
        # 去掉相关性大的特征
        final_select_proteins = self.remove_corr_feature(X_train.loc[:,select_proteins],select_proteins_import_df,biomarker_label_free_result_path)
        self.info_record("去掉相关性大的特征","计算特征筛选得到的特征两两之间相关性，以0.9为阈值，当两个特征之间的相关性阈值满足r>0.9时保留重要性大的特征，剔除重要性小的特征。最后得到的特征为："+str(final_select_proteins)+",一共有"+str(len(final_select_proteins))+"个基因。")
        # 根据新的测试数据集对生物标志物蛋白再一次筛选
        # 是否导入新的测试数据集
        final_X_test_prepared=None
        y_test = None
        test_data_path = gol.get_value("biomarker_label_free_test_data_path")
        test_information_path = gol.get_value("biomarker_label_free_test_information_path")
        if test_data_path is not None and test_information_path is not None:
            if if_applicable_newdata:
                new_if_gene_name = gol.get_value("biomarker_label_free_test_if_gene_name")
                if new_if_gene_name:
                    new_gene_col_name = gol.get_value("biomarker_label_free_test_gene_name")
                else:
                    new_gene_col_name = "Gene names"
                test_result,despri = handle_test_data(test_data_path, test_information_path, biomarker_label_free_result_path, biomarker_data_split_dirname,
                                 ngroup, pgroup, final_select_proteins,gene_col_name=new_gene_col_name)
                if test_result is None:
                    self.info_record("新的测试集数据无法使用：", despri)
                else:
                    final_X_test_prepared = test_result[0]
                    y_test = test_result[1]
                    final_select_proteins = test_result[2]
                    not_exist_select_proteins = test_result[3]
                    if len(not_exist_select_proteins)>0:
                        s = f"一共有{len(not_exist_select_proteins)}个基因在新的独立测试集中不存在，分别为：{not_exist_select_proteins},取在新的独立测试集存在表达信息的{len(final_select_proteins)}个基因作为建模的生物标志物组合，分别为：{final_select_proteins}."
                        self.info_record("筛选出的生物标志物与新的独立测试集中的基因求交集",
                             s)

            else:
                self.info_record("新的测试集数据无法使用", "原始数据与新的测试集数据的基因无法对应，两个数据集中都应该有'Gene names'列。")

        final_select_proteins_import_df = select_proteins_import_df.loc[final_select_proteins, :]
        final_select_proteins_import_df.index.name = complement_expression_df.index.name
        export_data(final_select_proteins_import_df, biomarker_label_free_result_path, biomarker_feature_select_dirname,
                    "final_features.xlsx", "final_features", complement_expression_df.loc[final_select_proteins, :])

        if test_set is not None:
            X_test = test_set.drop("class", axis=1)
            y_test = test_set["class"].copy()
            final_X_test_prepared = X_test.loc[:,final_select_proteins]

        final_X_train_prepared = X_train.loc[:,final_select_proteins]

        final_X_valid_prepared = None
        y_valid = None

        if verification_set is not None:
            X_valid = verification_set.drop("class", axis=1)
            y_valid = verification_set["class"].copy()
            final_X_valid_prepared = X_valid.loc[:, final_select_proteins]

        # 模型构建
        self.model_build_fuc(final_X_train_prepared, y_train, final_X_test_prepared,y_test,final_X_valid_prepared,y_valid, biomarker_label_free_result_path)

        # 运行结束
        self.over(start_time, True)

    def draw_table_fuc(self,result):
        describe_dict = {"score":"准确度","cm":"混淆矩阵","precision":"精度","recall":"召回率","f1_score":"F1分数","AUC":"AUC"}
        data = [["指标名称","指标的值"]]
        for key, value in result.items():
            name = describe_dict[key]
            data.append([name,str(value)])
        self.pdf.add_table(data)

    def get_smaller_importance_feature(self,feature_importance_df,feature1, feature2):
        if feature_importance_df.loc[feature1, "feature_importance"] >= feature_importance_df.loc[feature2, "feature_importance"]:
            return feature2
        else:
            return feature1

    def remove_corr_feature(self,X_prepared_df,feature_importance_df,biomarker_label_free_result_path):
        # 去掉相关性大的特征
        corr_df = X_prepared_df.corr()
        export_data(corr_df, biomarker_label_free_result_path, biomarker_feature_select_dirname,
                    "feature_correlation.xlsx", "feature correlation")
        remove_feature_names = []
        for i in corr_df.columns:
            if i not in remove_feature_names:
                features = corr_df.loc[corr_df[i] > 0.9, i].index
                for j in features:
                    if i != j:
                        smaller_importance_feature = self.get_smaller_importance_feature(feature_importance_df,i, j)
                        if smaller_importance_feature not in remove_feature_names:
                            remove_feature_names.append(smaller_importance_feature)
        feature_names = []
        for i in corr_df.columns:
            if i not in remove_feature_names:
                feature_names.append(i)
        return feature_names

    def model_build_fuc(self,final_X_train_prepared, y_train, final_X_test_prepared,y_test,final_X_valid_prepared,y_valid, biomarker_label_free_result_path):
        # 也可以不进行特征归一化
        scaler = StandardScaler().fit(final_X_train_prepared)
        final_X_train_prepared = pd.DataFrame(scaler.transform(final_X_train_prepared),columns=final_X_train_prepared.columns,index=final_X_train_prepared.index)
        export_data(final_X_train_prepared.T, biomarker_label_free_result_path, biomarker_data_split_dirname,
                    "train_set_scaler.xlsx", "train set")
        if final_X_test_prepared is not None:
            final_X_test_prepared = pd.DataFrame(StandardScaler().fit_transform(final_X_test_prepared),columns=final_X_test_prepared.columns,index=final_X_test_prepared.index)
            export_data(final_X_test_prepared.T, biomarker_label_free_result_path, biomarker_data_split_dirname,
                        "test_set_scaler.xlsx", "test set")
        if final_X_valid_prepared is not None:
            final_X_valid_prepared = pd.DataFrame(StandardScaler().fit_transform(final_X_valid_prepared),columns=final_X_valid_prepared.columns,index=final_X_valid_prepared.index)
            export_data(final_X_valid_prepared.T, biomarker_label_free_result_path, biomarker_data_split_dirname,
                        "valid_set_scaler.xlsx", "valid set")
        classifier_index = gol.get_value("biomarker_label_free_classifier_index")
        classifier_str = gol.get_value("biomarker_label_free_classifier")
        if classifier_index==5:
            classifier_str = "[随机森林, 非线性SVM, 朴素贝叶斯, 逻辑回归, 随机梯度下降分类]"
        self.info_record("模型构建","您选择的模型是:"+classifier_str+". ")
        # "随机森林", "非线性SVM", "朴素贝叶斯", "逻辑回归", "随机梯度下降分类", "以上所有"
        classifier_index_model = {0:{"随机森林":random_forest_model},1:{"非线性SVM":svm_model},2:{"朴素贝叶斯":naive_bayes_model},3:{"逻辑回归":lr_model},4:{"随机梯度下降分类":SGD_model},
                                  5:{"随机森林":random_forest_model,"非线性SVM":svm_model,"朴素贝叶斯":naive_bayes_model,"逻辑回归":lr_model,"随机梯度下降分类":SGD_model}}
        classifier_model_dict = classifier_index_model[classifier_index]
        model_dict = {}
        model_result_dict = {}
        dataset_type_name = "训练集"
        for model_name, model_fuc in classifier_model_dict.items():
            train_result_SGD, valid_result_SGD,model = model_fuc(final_X_train_prepared, y_train, final_X_valid_prepared,
                                                          y_valid, biomarker_label_free_result_path)
            model_dict[model_name]=model
            self.pdf.add_simple_title(model_name)
            self.pdf.add_simple_content("模型在训练集上效果指标如下表所示")
            self.draw_table_fuc(train_result_SGD)
            if valid_result_SGD is not None:
                dataset_type_name = "测试集"
                self.pdf.add_simple_content("模型在验证集上效果指标如下表所示")
                self.draw_table_fuc(valid_result_SGD)
                model_result_dict[model_name]=valid_result_SGD
            else:
                model_result_dict[model_name]=train_result_SGD
        # 根据AUC>F1分数>score>精度>召回率得到最佳的模型
        best_model_name_list = get_best_model_name(model_result_dict)
        self.info_record("最佳模型", "根据不同模型在"+dataset_type_name+"上的效果，选择出泛化较好的模型：" + str(best_model_name_list) + ". 接着在测试集上进一步探究模型的泛化效果。")
        for best_model_name in best_model_name_list:
            test_result =model_in_test(best_model_name, model_dict[best_model_name], final_X_test_prepared, y_test, biomarker_label_free_result_path, dirname=biomarker_model_dirname)
            self.pdf.add_simple_title(best_model_name)
            self.pdf.add_simple_content("模型在测试集上效果指标如下表所示")
            self.draw_table_fuc(test_result)

