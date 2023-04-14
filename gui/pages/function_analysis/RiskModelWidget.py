'''
富集分析：GO和KEGG
'''

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtCore import Qt

from gui.pages.function_analysis.MultiCoxWidget import MultiCoxWidget
from gui.pages.function_analysis.UniCoxWidget import UniCoxWidget


class RiskModelWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.tabs = QTabWidget()
        self.tab1 = UniCoxWidget()
        self.tab2 = MultiCoxWidget()

        # Add tabs
        self.tabs.addTab(self.tab1, "单因素cox回归")
        self.tabs.addTab(self.tab2, "多因素cox回归")

        layout.addWidget(self.tabs)