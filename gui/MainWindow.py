import os
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDesktopWidget, QWidget, QListWidget, QStackedWidget, QHBoxLayout, \
    QListWidgetItem, QSplitter
from gui.pages.IndexWidget import IndexWidget
from gui.pages.biomarker_analysis.BiomarkerLabelFreeWidget import BiomarkerLabelFreeWidget
from gui.pages.biomarker_analysis.BiomarkerMarkedWidget import BiomarkerMarkedWidget
from gui.pages.biomarker_analysis.BiomarkerWidget import BiomarkerWidget
from gui.pages.difference_analysis.IndexWidget import IndexWidget as DAIndexWidget
from gui.pages.difference_analysis.LabelFreeWidget import LabelFreeWidget
from gui.pages.difference_analysis.DIAWidget import DIAWidget
import util.Global as gol
from gui.pages.difference_analysis.MarkedWidget import MarkedWidget
from gui.pages.function_analysis.ClusterWidget import ClusterWidget
from gui.pages.function_analysis.EnrichWidget import EnrichWidget
from gui.pages.function_analysis.FunctionWidget import FunctionWidget
from gui.pages.function_analysis.RiskModelWidget import RiskModelWidget
from gui.pages.function_analysis.SurvivalWidget import SurvivalWidget
from gui.pages.function_analysis.WGCNAWidget import WGCNAWidget
from util.Logger import logger


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PPMarker平台')
        self.center_resize()

        self.initUI()

    def initUI(self):
        # 左右布局(左边一个QListWidget + 右边QStackedWidget)
        layout = QHBoxLayout(self, spacing=0)
        layout.setContentsMargins(0, 0, 0, 0)
        #实例化QSplitter控件并设置初始为水平方向布局 # 可以动态调整子窗口长度
        splitter1=QSplitter(Qt.Horizontal)
        # 左侧列表
        self.listWidget = QListWidget(self)
        splitter1.addWidget(self.listWidget)
        # 右侧层叠窗口
        self.stackedWidget = QStackedWidget(self)
        splitter1.addWidget(self.stackedWidget)

        splitter1.setSizes([gol.get_value("window_width")*0.14, gol.get_value("window_width")*0.85])
        layout.addWidget(splitter1)


        # 通过QListWidget的当前item变化来切换QStackedWidget中的序号
        # self.listWidget.currentRowChanged.connect(
        #     self.stackedWidget.setCurrentIndex)
        self.listWidget.currentRowChanged.connect(self.update_tab)
        self.listWidget.setStyleSheet(f"max-width: {gol.get_value('window_width')*0.2}px;min-width: 150px;")

        # 去掉边框
        self.listWidget.setFrameShape(QListWidget.NoFrame)
        # 隐藏滚动条
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 这里就用一般的文本配合图标模式了(也可以直接用Icon模式,setViewMode)
        ResourcePath = gol.get_value("ResourcePath")
        icon_path = os.path.join(ResourcePath, "img")
        LeftTabDict = gol.get_value("LeftTabDict")
        for key in LeftTabDict.keys():
            path = os.path.join(icon_path,"icon", "01.ico" )
            item = QListWidgetItem(QIcon(path), key, self.listWidget)
            # 设置item的默认宽高(这里只有高度比较有用)
            item.setSizeHint(QSize(16777215, int(gol.get_value("window_height")/25)))
            # 文字居中
            item.setTextAlignment(Qt.AlignCenter)
            for i in  LeftTabDict[key]:
                subItem = QListWidgetItem(i, self.listWidget)
                subItem.setSizeHint(QSize(16777215, int(gol.get_value("window_height")/25-10)))
                subItem.setTextAlignment(Qt.AlignCenter)

        # 默认页面为首页
        self.listWidget.setCurrentRow(0)
        self.stackedWidget.setCurrentIndex(0)

        #     首页
        # self.stackedWidget.addWidget(IndexWidget())
        # 差异分析
        self.stackedWidget.addWidget(DAIndexWidget())
        # DIA数据处理
        self.stackedWidget.addWidget(DIAWidget())
        # 无标记定量
        self.stackedWidget.addWidget(LabelFreeWidget())
        # TMT标记定量
        self.stackedWidget.addWidget(MarkedWidget())
        # 生物标志物筛选
        self.stackedWidget.addWidget(BiomarkerWidget())
        # 生物标志物筛选:无标记定量
        self.stackedWidget.addWidget(BiomarkerLabelFreeWidget())
        # 生物标志物筛选:标记定量
        self.stackedWidget.addWidget(BiomarkerMarkedWidget())
        # 功能分析
        self.stackedWidget.addWidget(FunctionWidget())
        # 富集分析
        self.stackedWidget.addWidget(EnrichWidget())
        # 聚类分析
        self.stackedWidget.addWidget(ClusterWidget())
        # 生存分析
        self.stackedWidget.addWidget(RiskModelWidget())
        self.stackedWidget.addWidget(SurvivalWidget())
        # # k均值聚类
        # self.stackedWidget.addWidget(KMeansWidget())

    def center_resize(self):
        """
        调整窗口大小为屏幕的宽高的0.75倍，窗口位置居中显示
        """
        screen = QDesktopWidget().screenGeometry()
        window_width = int(screen.width() * 0.85)
        window_height = int(screen.height() * 0.85)
        logger.info(f"窗口的高度与宽度：{window_height, window_width}")
        gol.set_value("window_width",window_width)
        gol.set_value("window_height",window_height)
        self.setGeometry(100, 100, window_width, window_height)
        form = self.geometry()
        x_move_step = int((screen.width() - form.width()) / 2)
        y_move_step = int((screen.height() - form.height()) / 2)
        self.move(x_move_step, y_move_step)

    def update_tab(self,index):
        # 定义页面对应关系
        # index_list = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
        self.stackedWidget.setCurrentIndex(index)#根据文本设置不同的页面
