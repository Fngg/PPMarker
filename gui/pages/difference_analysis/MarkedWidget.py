from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtCore import Qt

from gui.pages.difference_analysis.MarkedPhoWidget import MarkedPhoWidget
from gui.pages.difference_analysis.MarkedProWidget import MarkedProWidget


class MarkedWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.tabs = QTabWidget()
        self.tab1 = MarkedProWidget()
        self.tab2 = MarkedPhoWidget()

        # Add tabs
        self.tabs.addTab(self.tab1, "蛋白质组学")
        self.tabs.addTab(self.tab2, "磷酸化组学")

        layout.addWidget(self.tabs)