from PyQt5.QtCore import QThread, pyqtSignal
import time
import pandas as pd
from service.FileService import readFile
from service.function_analysis.KMSurvivalService import km_survival
from util.Logger import logger
import util.Global as gol
import os
import numpy as np


class KmSurvivalQThread(QThread):
    # 失败时传出信号
    error_trigger = pyqtSignal(str)
    # 正常运行过程中的日志输出
    info_trigger = pyqtSignal(str, str)

    def __int__(self):
        super(KmSurvivalQThread, self).__init__()

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
        logger.debug("KM生存分析分析开始")
        km_survival_result_path = gol.get_value("km_survival_result_path")
        km_survival_data_path = gol.get_value("km_survival_data_path")
        km_survival_survival_time = gol.get_value("km_survival_survival_time")
        km_survival_survival_status = gol.get_value("km_survival_survival_status")
        km_survival_survival_time_type = gol.get_value("km_survival_survival_time_type")

        if os.path.exists(km_survival_result_path) and os.path.exists(km_survival_data_path):
            km_survival_data = readFile(km_survival_data_path,if_zero_na=False)
            number_cols = km_survival_data.select_dtypes(["number"]).columns
            if km_survival_survival_time not in number_cols:
                self.error_trigger.emit(f"您选择的生存时间{km_survival_survival_time}的值不是数值化数据")
                self.over(start_time, False)
                return None
            if km_survival_survival_status not in number_cols:
                self.error_trigger.emit(f"您选择的生存状态{km_survival_survival_status}的值不是数值化数据")
                self.over(start_time, False)
                return None
            # 去掉生存状态和生存时间为空的样本
            km_survival_data3 = km_survival_data.dropna(axis=0, subset=[km_survival_survival_time, km_survival_survival_status])
            remove_indexs = set(km_survival_data.index).difference(set(km_survival_data3.index))
            if len(remove_indexs) > 0:
                self.info_record("去掉生存时间或生存状态为空的样本", str(remove_indexs))
            # 判断生存状态是否仅为0与1
            survival_status_values =  km_survival_data3[km_survival_survival_status].unique()
            if len(survival_status_values)==2 and (1 in survival_status_values) and (0 in survival_status_values):
                if km_survival_survival_time_type=="month":
                    km_survival_data3[km_survival_survival_time]= km_survival_data3[km_survival_survival_time]/12
                elif km_survival_survival_time_type=="day":
                    km_survival_data3[km_survival_survival_time]= km_survival_data3[km_survival_survival_time]/365
                # 对km_survival_data3的列进行遍历，对于二分类和离散型的特征进行KM曲线绘制，其他的特征列忽略
                survival_plot_dir = os.path.join(km_survival_result_path, "survival_plot")
                if not os.path.exists(survival_plot_dir):
                    os.mkdir(survival_plot_dir)
                p_df = pd.DataFrame(columns=["feature","Logrank Pvalue"])
                for col in km_survival_data3.columns:
                    if col != km_survival_survival_time and col!=km_survival_survival_status:
                        tmp_data = km_survival_data3.dropna(axis=0, subset=[col])[[km_survival_survival_time,km_survival_survival_status,col]]
                        # 说明该列是基因的表达值或者是年龄什么的
                        if len(tmp_data[col].unique()) == 2:
                            # 二分类变量
                            logrank_p = km_survival(tmp_data,col,km_survival_survival_time,km_survival_survival_status,km_survival_result_path,bi=True)
                        elif issubclass(tmp_data[col].dtypes.type,np.number):
                            # 连续变量
                            logrank_p = km_survival(tmp_data, col, km_survival_survival_time,
                                                    km_survival_survival_status, km_survival_result_path, bi=False)
                        else:
                            self.info_record("特征忽略",f"{col}的特征值非二分类变量也非连续性数值变量，不做KM生存分析，忽略该特征。")
                            logrank_p = None
                        sub_p = pd.Series({"feature":col,"Logrank Pvalue":logrank_p})
                        p_df = p_df.append(sub_p,ignore_index=True)
                logrank_p_result_path = os.path.join(km_survival_result_path,"logrank_p_result.csv")
                p_df["impact_survival"] = p_df.apply(lambda x: "YES" if x["Logrank Pvalue"]<0.05 else "NO", axis=1)
                p_df.to_csv(logrank_p_result_path,index=False)
                # # 运行结束
                self.over(start_time, True)
            else:
                self.error_trigger.emit(f"您选择的生存状态{km_survival_survival_status}列的值不只为0与1")
                self.over(start_time, False)
                return None
        else:
            self.error_trigger.emit("导入的表达数据或结果文件夹不存在")
            self.over(start_time, False)
            return None
