'''
富集分析：GO和KEGG
'''

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtCore import Qt
from gui.pages.function_analysis.KMeansWidget import KMeansWidget
from gui.pages.function_analysis.WGCNAWidget import WGCNAWidget


class ClusterWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.step = 1

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.tabs = QTabWidget()
        self.tab1 = KMeansWidget()
        self.tab2 = WGCNAWidget()

        # Add tabs
        self.tabs.addTab(self.tab1, "K均值聚类分析")
        self.tabs.addTab(self.tab2, "WGCNA分析")

        layout.addWidget(self.tabs)
