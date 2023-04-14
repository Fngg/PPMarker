from PyQt5.QtWidgets import QWidget,QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout,QMessageBox,QFileDialog,QComboBox
from PyQt5.QtCore import Qt
from gui.mywidgets.MyQLable import MyQLabel
from gui.workQThead.FileQThead import SaveMLTemplateThead
from gui.workQThead.EnrichAnalysisQThead import ClusterQThead
import util.Global as gol
import os


class KMeansWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        mainlayout = QVBoxLayout(self)
        mainlayout.setAlignment(Qt.AlignTop)

        hLayout = QHBoxLayout()
        hLayout.setSpacing(20)
        label4 = QLabel("1. 导入表达数据",self)
        label2 = MyQLabel("下载模板数据",self)
        label2.setStyleSheet("color:red;text-decoration:underline;")
        label2.connect_customized_slot(self.saveFile)

        dataInputBtn = QPushButton(
            '导入原始文件', self, objectName='ClickBtn')
        dataInputBtn.setStyleSheet("background: #83c5be")
        dataInputBtn.clicked.connect(self.openFile)

        hLayout.addWidget(label4)
        hLayout.addWidget(label2)
        hLayout.addWidget(dataInputBtn)
        hLayout.addStretch(1)

        layout = QHBoxLayout()
        # 控件添加到水平布局中
        layout.setSpacing(10)
        label2 = QLabel("2. 选择的聚类分析方法：", self)
        self.clusterMethod = QComboBox(self, minimumWidth=200)
        self.clusterMethod.addItems(["K-Means-Cluster", "Fuzzy C-Means"])
        layout.addWidget(label2)
        layout.addWidget(self.clusterMethod)
        layout.addStretch(1)

        layout3 = QHBoxLayout()
        layout3.setSpacing(10)
        label3 = QLabel("3. 选择输出结果路径： ",self)
        self.saveFileBtn = QPushButton('路径选择', self, objectName='ClickBtn')
        self.saveFileBtn.setStyleSheet("background: #83c5be")
        self.saveFileBtn.clicked.connect(self.saveFilePath)
        layout3.addWidget(label3)
        layout3.addWidget(self.saveFileBtn)
        layout3.addStretch(1)

        certainBtn = QPushButton('确定', self, objectName='ClickBtn')
        certainBtn.setStyleSheet("background: #83c5be;max-width: 120px;")
        certainBtn.clicked.connect(self.certain)

        self.resultEdit = QTextEdit(self)
        self.resultEdit.setReadOnly(True)

        mainlayout.addLayout(hLayout)
        mainlayout.addLayout(layout)
        mainlayout.addLayout(layout3)
        mainlayout.addWidget(certainBtn)
        mainlayout.addWidget(self.resultEdit)

    def saveFile(self):
        fileName, ftype = QFileDialog.getSaveFileName(self, 'save file', 'expression.xlsx', "*.xlsx")
        if fileName:
            gol.set_value("MLDataTemplateFile", fileName)
            self.saveMLTemplateThead = SaveMLTemplateThead()
            self.saveMLTemplateThead.start()

    def openFile(self):
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                                   "(*.csv *.xlsx *.xls)")
        if fileName is not None and fileName != "":
            self.resultEdit.append("=========================分割线=============================")
            self.resultEdit.append("导入原始数据, 文件路径为：" + fileName)
            gol.set_value("ClusterFilePath", fileName)

    def saveFilePath(self):
        directory = QFileDialog.getExistingDirectory(self, "file Path", "")
        if directory is not None and directory != "":
            gol.set_value("ClusterResultPath", directory)
            self.resultEdit.append("=========================分割线=============================")
            self.resultEdit.append("您选择的输出结果文件路径为：" + directory)

    def certain(self):
        clusterFilePath = gol.get_value("ClusterFilePath")
        clusterResultPath = gol.get_value("ClusterResultPath")
        if clusterFilePath and clusterResultPath:
            clusterMethod = self.clusterMethod.currentText()
            self.resultEdit.append("=========================分割线=============================")
            self.resultEdit.append("您选择的聚类分析方法为：" + clusterMethod)
            gol.set_value("ClusterMethod",clusterMethod)
            self.clusterQThead = ClusterQThead()
            self.clusterQThead.trigger.connect(self.display)
            self.clusterQThead.start()
        else:
            QMessageBox.warning(self, "提示", "请先导入数据")

    def display(self,time, ifSucess):
        if ifSucess:
            self.resultEdit.append("聚类分析生成成功,总运行时间：%f s" %time)
            fileName = gol.get_value("ClusterResultPath")
            self.resultEdit.append("聚类分析结果文件地址：%s"%(fileName+"/k-means-result.pdf; "+fileName+"/k_means_result.xlsx"))
        else:
            self.resultEdit.append("聚类分析失败")