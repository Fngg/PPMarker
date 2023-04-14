from PyQt5.QtCore import QThread, pyqtSignal
import time
from service.FunctionRcodeService import goOrKegg,wgcna1,wgcna2,wgcna3
from util.Logger import logger
from service.FileService import readFile
from service.ClusterServiceOld import k_means,fuzzy_c_means
import util.Global as gol


class EnrichAnalysisQThead(QThread):
    # 定义一个信号
    trigger = pyqtSignal(float,bool)

    def __int__(self):
        # 初始化函数，默认
        super(EnrichAnalysisQThead, self).__init__()

    def run(self):
        start_time = time.time()
        result = goOrKegg()
        if not result:
            logger.warning("GO/KEGG富集分析失败")
        end_time = time.time()
        self.trigger.emit((end_time - start_time), result)


class WGCNAAnalysisQThead(QThread):
    # 定义一个信号
    trigger = pyqtSignal(float,bool,str)

    def __int__(self):
        # 初始化函数，默认
        super(WGCNAAnalysisQThead, self).__init__()

    def run(self):
        start_time = time.time()
        result1 = wgcna1()
        end_time1 = time.time()
        self.trigger.emit((end_time1 - start_time), result1,"数据前处理")
        if not result1:
            logger.warning("数据前处理失败")
            return None

        result2 = wgcna2()
        end_time2 = time.time()
        self.trigger.emit((end_time2 - end_time1), result2, "WGCNA网络构建")
        if not result2:
            logger.warning("WGCNA网络构建失败")
            return None

        result3 = wgcna3()
        end_time3 = time.time()
        self.trigger.emit((end_time3 - end_time2), result3, "探究性状与模型的关系")
        if not result2:
            logger.warning("探究性状与模型的关系失败")


class ClusterQThead(QThread):
    # 定义一个信号
    trigger = pyqtSignal(float,bool)

    def __int__(self):
        # 初始化函数，默认
        super(ClusterQThead, self).__init__()

    def run(self):
        start_time = time.time()
        clusterFilePath = gol.get_value("ClusterFilePath")
        clusterResultPath = gol.get_value("ClusterResultPath")
        ClusterMethod = gol.get_value("ClusterMethod")
        df = readFile(clusterFilePath,if_zero_na=True,index_col=0)
        if "K" in ClusterMethod:
            result = k_means(df,clusterResultPath)
        else:
            result = fuzzy_c_means(df,clusterResultPath)
        end_time1 = time.time()
        self.trigger.emit((end_time1 - start_time), result)




