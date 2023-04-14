'''
富集分析：GO和KEGG
'''

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtCore import Qt
from gui.pages.function_analysis.GOKEGGEnrichWidget import GOKEGGEnrichWidget
from gui.pages.function_analysis.GSEAEnrichWidget import GSEAEnrichWidget


class EnrichWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.step = 1

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.tabs = QTabWidget()
        self.tab1 = GOKEGGEnrichWidget()
        self.tab2 = GSEAEnrichWidget()

        # Add tabs
        self.tabs.addTab(self.tab1, "GO和KEGG富集分析")
        self.tabs.addTab(self.tab2, "GSEA富集分析")

        layout.addWidget(self.tabs)
