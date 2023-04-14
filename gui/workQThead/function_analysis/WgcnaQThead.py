'''
go和kegg富集分析：
1. 首先发送enrich_analysis请求
2. 多次发送enrich_analysis_ready请求，直到返回准备好
3. 下载数据enrich_analysis_download
4. 删掉服务器上的数据文件enrich_analysis_remove
'''
from PyQt5.QtCore import QThread, pyqtSignal
import time

from service.FileService import readFile
from service.R_service.wgcna_service import wgcna_service
from util.Logger import logger
import util.Global as gol
import os



def retry_on_result_fuc(result):
    return result == False


class WGCNAQThread(QThread):
    # 失败时传出信号
    error_trigger = pyqtSignal(str)
    # 正常运行过程中的日志输出
    info_trigger = pyqtSignal(str, str)

    def __int__(self):
        super(WGCNAQThread, self).__init__()
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

    def info_record(self, step, text):
        self.info_trigger.emit(step, text)

    def run(self):
        try:
            self._run()
        except Exception as e:
            # 日志记录
            logger.exception("Exception Logged")
            # self.exc_traceback = ''.join(traceback.format_exception(*sys.exc_info()))
            self.error_trigger.emit(repr(e))

    def _run(self):
        start_time = time.time()
        logger.debug("WGCNA分析开始")
        wgcna_interested_trait = gol.get_value("wgcna_interested_trait")
        wgcna_information_path = gol.get_value("wgcna_information_path")
        wgcna_expression_path = gol.get_value("wgcna_expression_path")
        wgcna_result_path = gol.get_value("wgcna_result_path")
        if not os.path.exists(wgcna_result_path):
            self.error_trigger.emit("输出结果的文件夹不存在")
            self.over(start_time, False)
            return None
        wgcna_expression_df = readFile(wgcna_expression_path,if_zero_na=False)
        wgcna_information_df = readFile(wgcna_information_path,if_zero_na=False)
        # 判断样本名称是否一样
        if not set(wgcna_expression_df.columns)==set(wgcna_information_df.index):
            # 取样本交集
            inter_simples = list(set(wgcna_expression_df.columns).intersection(set(wgcna_information_df.index)))
            self.info_record("表达数据与表型数据中样本不对应", "取表达数据与表型数据中样本交集，一共有"+str(len(inter_simples))+"个样本。")
            wgcna_expression_df = wgcna_expression_df.loc[:,inter_simples]
            wgcna_information_df = wgcna_information_df.loc[inter_simples,:]
        # 选择数值型的数据
        wgcna_information_df2 = wgcna_information_df.select_dtypes(["number"])
        remove_cols = set(wgcna_information_df.columns).difference(set(wgcna_information_df2.columns))
        if len(remove_cols)>0:
            self.info_record("去掉非数值的表型特征",str(remove_cols))
        if wgcna_interested_trait not in wgcna_information_df2.columns:
            self.error_trigger.emit("您选择的感兴趣表型特征在数值化的表型数据中不存在")
            self.over(start_time, False)
            return None

        wgcna_service(wgcna_expression_df, wgcna_information_df2, wgcna_interested_trait, wgcna_result_path)
        # # 运行结束
        self.over(start_time, True)

