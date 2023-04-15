from PyQt5.QtWidgets import QApplication
import sys,os
import util.Global as gol
from util.Logger import logger
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib as mpl
import platform


if __name__ == '__main__':
    # 设置R的系统环境
    can_use_r = True
    system_type = platform.system()
    if system_type=="Windows":
        withR = True
        if withR:
            path = "../software/R-4.2.1"
            if not os.path.exists(path):
                path = "./R-4.2.1"
            if os.path.exists(path):
                os.environ['R_HOME'] =path
                if "R-4.2.1" not in os.environ['path']:
                    os.environ["PATH"] = path+"/bin/x64" + ";" + os.environ["PATH"]
                logger.info(f"R已经配置好，path:{path}")
            else:
                logger.info("系统中没有安装R，无法使用关于R的功能")
                can_use_r=False
        else:
            if "R-" not in os.environ['path']:
                logger.info("系统中没有安装R，无法使用关于R的功能")
                can_use_r=False

        if "Graphviz" not in os.environ['path']:
            path_graph = "../software/Graphviz/bin"
            if not os.path.exists(path_graph):
                path_graph = "../Graphviz/bin"
            if not os.path.exists(path_graph):
                path_graph = "./Graphviz/bin"
            logger.info(f"path_graph:{path_graph}")
            if os.path.exists(path_graph):
                os.environ['path'] = os.environ['path']+";"+path_graph+";"
            else:
                logger.error("Graphviz软件没有安装，请先安装Graphviz")
    elif system_type=="Linux":
        # linux 系统
        can_use_r=True
    # 初始化变量
    from gui.MainWindow import MainWindow
    mpl.rc_file_defaults()
    logger.debug("初始化Global变量")
    RootPath = os.path.abspath(os.path.dirname(__file__))
    ResourcePath = os.path.join(RootPath, "resources")
    LeftTabDict = {"差异分析":["DIA数据处理","无标记定量", "标记定量"],"标志物筛选":["无标记定量", "标记定量"],"功能分析":["富集分析","聚类分析","构建风险模型","生存分析"]}
    gol._init()
    gol.set_value("RootPath",RootPath)
    gol.set_value("ResourcePath",ResourcePath)
    gol.set_value("LeftTabDict",LeftTabDict)
    gol.set_value("can_use_r",can_use_r)

    # 设置输出结果pdf的字体
    font_path = os.path.join(ResourcePath, "css", "SimSun.ttf")
    pdfmetrics.registerFont(TTFont('SimSun', font_path))

    logger.debug("软件开始启动")
    app = QApplication(sys.argv)
    stylesheetFile = os.path.join(ResourcePath,"css","application.css")
    with open(stylesheetFile,encoding='utf-8') as f:
        app.setStyleSheet(f.read())
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

