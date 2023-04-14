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
from service.R_service.go_kegg_service import go_kegg_service
from util.Logger import logger
import util.Global as gol
from util.Http import HTTPPlatform
import os
import json
from retrying import retry


def retry_on_result_fuc(result):
    return result == False


class EnrichQThread(QThread):
    # 失败时传出信号
    error_trigger = pyqtSignal(str)
    # 正常运行过程中的日志输出
    info_trigger = pyqtSignal(str, str)

    def __int__(self):
        super(EnrichQThread, self).__init__()
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
        logger.debug("go和kegg富集分析开始")
        enrich_org_type = gol.get_value("enrich_org_type")
        enrich_gene_type = gol.get_value("enrich_gene_type")
        enrich_data_path = gol.get_value("enrich_data_path")
        enrich_result_path = gol.get_value("enrich_result_path")
        if not os.path.exists(enrich_result_path):
            self.error_trigger.emit("输出结果的文件夹不存在")
            self.over(start_time, False)
            return None
        enrich_df = readFile(enrich_data_path,if_zero_na=False,index_col=None)
        enrich_df_cols = enrich_df.columns.tolist()
        if len(enrich_df_cols)==1 and enrich_df_cols[0] in ("Gene names_No.","Gene names"):
            if enrich_df_cols[0]=="Gene names_No.":
                genes = []
                for gene_no in enrich_df["Gene names_No."]:
                    gene = gene_no.rsplit("_",1)[0]
                    genes.append(gene)
            else:
                genes= enrich_df["Gene names"].tolist()
            self.info_record("Go和KEGG富集分析", "分析开始")
            go_kegg_service(enrich_org_type, enrich_gene_type, genes, enrich_result_path)
            # 运行结束
            self.over(start_time, True)
        else:
            self.error_trigger.emit("您导入的基因文件格式不正确")
            self.over(start_time, False)
            return None


