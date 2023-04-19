from PyQt5.QtCore import QThread, pyqtSignal
import time

from service.FileService import readFile
from service.R_service.cox_service import multicox_service
from util.Logger import logger
import util.Global as gol
import os


class MultiCoxQThread(QThread):
    # 失败时传出信号
    error_trigger = pyqtSignal(str)
    # 正常运行过程中的日志输出
    info_trigger = pyqtSignal(str, str)

    def __int__(self):
        super(MultiCoxQThread, self).__init__()

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
        logger.debug("多因素cox回归分析开始")
        multicox_result_path = gol.get_value("multicox_result_path")
        multicox_data_path = gol.get_value("multicox_data_path")
        multicox_survival_time = gol.get_value("multicox_survival_time")
        multicox_survival_status = gol.get_value("multicox_survival_status")
        multicox_survival_time_type = gol.get_value("multicox_survival_time_type")
        if os.path.exists(multicox_result_path) and os.path.exists(multicox_data_path):
            multicox_data = readFile(multicox_data_path,if_zero_na=False)
            multicox_data2 = multicox_data.select_dtypes(["number"])
            remove_cols = set(multicox_data.columns).difference(set(multicox_data2.columns))
            if len(remove_cols) > 0:
                self.info_record("去掉非数值的列", str(remove_cols))
            if multicox_survival_time not in multicox_data2.columns:
                self.error_trigger.emit(f"您选择的生存时间{multicox_survival_time}在数值化的数据中不存在")
                self.over(start_time, False)
                return None
            if multicox_survival_status not in multicox_data2.columns:
                self.error_trigger.emit(f"您选择的生存状态{multicox_survival_status}在数值化的数据中不存在")
                self.over(start_time, False)
                return None
            # 去掉生存状态和生存时间为空的样本
            multicox_data3 = multicox_data2.dropna(axis=0, subset=[multicox_survival_time, multicox_survival_status])
            remove_indexs = set(multicox_data2.index).difference(set(multicox_data3.index))
            if len(remove_indexs) > 0:
                self.info_record("去掉生存时间或生存状态为空的样本", str(remove_indexs))
            # 判断生存状态是否仅为0与1
            survival_status_values =  multicox_data3[multicox_survival_status].unique()
            if len(survival_status_values)==2 and (1 in survival_status_values) and (0 in survival_status_values):
                if multicox_survival_time_type=="month":
                    multicox_data3[multicox_survival_time]= multicox_data3[multicox_survival_time]/30
                elif multicox_survival_time_type=="day":
                    multicox_data3[multicox_survival_time]= multicox_data3[multicox_survival_time]/365
                multicox_data3 = multicox_data3.rename(columns={multicox_survival_time: 'OS',multicox_survival_status:"status"})

                multicox_if_enrich = gol.get_value("multicox_if_enrich")
                multicox_service(multicox_data3,multicox_result_path,multicox_if_enrich)
                # # 运行结束
                self.over(start_time, True)
            else:
                self.error_trigger.emit(f"您选择的生存状态{multicox_survival_status}列的值不只为0与1")
                self.over(start_time, False)
                return None
        else:
            self.error_trigger.emit("导入的表达数据或结果文件夹不存在")
            self.over(start_time, False)
            return None
