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
from service.R_service.gesa_service import gsea_service
from util.Logger import logger
import util.Global as gol
import pandas as np
import os


def retry_on_result_fuc(result):
    return result == False


class GSEAQThread(QThread):
    # 失败时传出信号
    error_trigger = pyqtSignal(str)
    # 正常运行过程中的日志输出
    info_trigger = pyqtSignal(str, str)

    def __int__(self):
        super(GSEAQThread, self).__init__()
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
        logger.debug("GSEA富集分析开始")
        enrich_org_type = gol.get_value("gsea_org_type")
        enrich_gene_type = gol.get_value("gsea_gene_type")
        enrich_data_path = gol.get_value("gsea_data_path")
        enrich_result_path = gol.get_value("gsea_result_path")
        if not os.path.exists(enrich_result_path):
            self.error_trigger.emit("输出结果的文件夹不存在")
            self.over(start_time, False)
            return None
        enrich_df = readFile(enrich_data_path,index_col=None,if_zero_na=False)
        enrich_df_cols = enrich_df.columns.tolist()
        if len(enrich_df_cols)==2 :
            if enrich_df_cols[0]=="Gene" and enrich_df_cols[1] in ("logFC","FoldChange"):
                enrich_df.rename(columns={'Gene':enrich_gene_type},inplace=True)
                if enrich_df_cols[1]=="FoldChange":
                    enrich_df["logFC"] = enrich_df.apply(lambda row: np.log2(row["FoldChange"]),
                          axis=1)
                    enrich_df.drop(columns="FoldChange",inplace=True)
                self.info_record("GSEA富集分析", "分析开始")
                gsea_service(enrich_org_type, enrich_gene_type, enrich_df, enrich_result_path)
                # 运行结束
                self.over(start_time, True)
            else:
                self.error_trigger.emit("您导入的基因文件格式不正确，请按照例子中数据格式填写。")
                self.over(start_time, False)
                return None
        else:
            self.error_trigger.emit("您导入的基因文件格式不正确，请按照例子中数据格式填写。")
            self.over(start_time, False)
            return None


