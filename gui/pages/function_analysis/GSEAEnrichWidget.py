'''
富集分析：GO和KEGG
'''

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
    QTextEdit, QLabel, QPushButton, QComboBox, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt
import os
import util.Global as gol
from gui.mywidgets.MyQLable import MyQLabel
from gui.workQThead.UtilThread import CopyFileThread
from gui.workQThead.function_analysis.GSEAQThead import GSEAQThread


class GSEAEnrichWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.step = 1

    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 10, 10)

        vLayout1 = QVBoxLayout()
        vLayout1.setSpacing(10)

        label2 = QLabel("分析进展", self)
        self.resultEdit = QTextEdit(self)
        self.resultEdit.setReadOnly(True)
        self.resultEdit.append('''当传统的GO、KEGG富集分析在差异基因上富集不到结果时，可以采用GSEA富集分析。GSEA富集分析不是基于差异基因，而是采用全部基因作为输入。GO，KEGG分析更加依赖差异基因，实则是对一部分基因的分析，忽略差异不显著的基因，而GSEA是从全体基因的表达矩阵中找出具有协同差异的基因集，故能兼顾差异较小的基因。GSEA分析不需要指定阈值（p值或FDR）来筛选差异基因，在没有经验存在的情况下分析我们感兴趣的基因集，而这个基因集不一定是显著差异表达的基因。\n\n基因排序数据：如差异分析后的数据，只需要基因名和FoldChange（或者log2FC）两列。
        ''')

        vLayout1.addWidget(label2)
        vLayout1.addWidget(self.resultEdit)

        vLayout2 = QVBoxLayout()
        vLayout2.setSpacing(10)
        vLayout2.setAlignment(Qt.AlignTop)

        label3 = QLabel("基因排序数据导入", self)
        label3.setStyleSheet("font-weight:bold")

        hLayout1 = QHBoxLayout()
        hLayout1.setSpacing(20)
        dataInputBtn = QPushButton(
            '基因排序数据', self, objectName='ClickBtn')
        dataInputBtn.setStyleSheet("background: #83c5be")
        dataInputBtn.clicked.connect(self.enrich_data_import)
        label4 = MyQLabel("下载基因排序数据模板", self)
        label4.setStyleSheet("color:red;text-decoration:underline;")
        label4.connect_customized_slot(lambda: self.saveFile("GSEA-rank-data.xlsx"))
        hLayout1.addWidget(dataInputBtn)
        hLayout1.addWidget(label4)
        hLayout1.addStretch(1)

        label61 = QLabel("设置参数", self)
        label61.setStyleSheet("font-weight:bold")

        hLayout71 = QHBoxLayout()
        hLayout71.setSpacing(10)
        label71 = QLabel("物种：", self)
        self.oriQComboBox = QComboBox(self, minimumWidth=200)
        self.oriQComboBox.addItems(["Homo Sapiens(9606)", "Mus Musculus(10090)"])
        hLayout71.addWidget(label71)
        hLayout71.addWidget(self.oriQComboBox)
        hLayout71.addStretch(1)

        hLayout72 = QHBoxLayout()
        hLayout72.setSpacing(10)
        label72 = QLabel("基因格式：", self)
        self.geneTypeColname = QComboBox(self, minimumWidth=200)
        self.geneTypeColname.addItems(["Symbol", "Entrez ID", "Ensembl gene ID"])
        hLayout72.addWidget(label72)
        hLayout72.addWidget(self.geneTypeColname)
        hLayout72.addStretch(1)

        label11 = QLabel("结果导出", self)
        label11.setStyleSheet("font-weight:bold")

        hLayout7 = QHBoxLayout()
        hLayout7.setSpacing(10)
        label10 = QLabel("输出结果路径：", self)
        self.saveFileBtn = QPushButton('路径选择', self, objectName='ClickBtn')
        self.saveFileBtn.setStyleSheet("background: #83c5be")
        self.saveFileBtn.clicked.connect(self.save_result)
        hLayout7.addWidget(label10)
        hLayout7.addWidget(self.saveFileBtn)
        hLayout7.addStretch(1)

        certainBtn = QPushButton('确定', self, objectName='ClickBtn')
        certainBtn.setStyleSheet("background: #83c5be;max-width: 120px;")
        certainBtn.clicked.connect(self.certain)

        vLayout2.addWidget(label3)
        vLayout2.addLayout(hLayout1)
        vLayout2.addWidget(label61)
        vLayout2.addLayout(hLayout71)
        vLayout2.addLayout(hLayout72)
        vLayout2.addWidget(label11)
        vLayout2.addLayout(hLayout7)
        vLayout2.addWidget(certainBtn)

        layout.addLayout(vLayout1, stretch=6)
        layout.addLayout(vLayout2, stretch=4)


    def saveFile(self, exit_file_name):
        file_type = exit_file_name.split(".")[-1]
        to_file_path, ftype = QFileDialog.getSaveFileName(self, 'save file', exit_file_name, "*." + file_type)
        if to_file_path:
            ResourcePath = gol.get_value("ResourcePath")
            exit_file_path = os.path.join(ResourcePath, "file", "function_analysis", exit_file_name)
            t = CopyFileThread(exit_file_path, to_file_path)  # 目标函数
            t.start()  # 启动线程

    def save_result(self):
        '''
        设置保存结果位置
        '''
        directory = QFileDialog.getExistingDirectory(self, "file Path", "")
        if directory is not None and directory != "":
            gol.set_value("gsea_result_path", directory)
            self.resultEdit.append(str(self.step) + ".结果路径：" + directory)
            self.step += 1

    def enrich_data_import(self):
        '''
        导入差异基因进行富集分析
        '''
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                         "(*.txt *.csv *.xlsx *.xls *.tsv)")
        if fileName is not None and fileName != "":
            self.resultEdit.append(str(self.step) + ".导入的基因文件：" + fileName)
            self.step += 1
            gol.set_value("gsea_data_path", fileName)

    def info_display(self, step, text):
        '''
        分析过程中的正常日志打印
        step:操作步骤
        text：当前步骤的运行结果
        '''
        self.resultEdit.append(step + " :" + text)

    def error_display(self, text):
        '''
        text:失败信息
        '''
        self.resultEdit.append("运行失败，错误原因：" + text)
        QMessageBox.warning(self, "发生错误", text)

    def certain(self):
        if gol.get_value("gsea_data_path") and gol.get_value("gsea_result_path"):
            org_type_index = self.oriQComboBox.currentIndex()
            if org_type_index == 0:
                enrichOrgType = "hsa"
            else:
                enrichOrgType = "mmu"
            gene_type_index = self.geneTypeColname.currentIndex()
            if gene_type_index == 0:
                enrichGeneType = "SYMBOL"
            elif gene_type_index == 1:
                enrichGeneType = "ENTREZID"
            else:
                enrichGeneType = "ENSEMBL"
            gol.set_value("gsea_org_type", enrichOrgType)
            gol.set_value("gsea_gene_type", enrichGeneType)
            self.resultEdit.append(str(self.step) + ".数据分析中...")
            self.main_thread = GSEAQThread()
            self.main_thread.error_trigger.connect(self.error_display)
            self.main_thread.info_trigger.connect(self.info_display)
            self.main_thread.start()
        else:
            QMessageBox.warning(self, "提示", "请先导入数据和设置结果路径！")
