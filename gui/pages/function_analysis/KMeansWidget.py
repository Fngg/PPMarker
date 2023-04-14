from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QButtonGroup, \
    QTextEdit, QLabel, QPushButton, QComboBox, QMessageBox, QFileDialog, QRadioButton, QSpinBox, QDialog
from PyQt5.QtCore import Qt
import os
import util.Global as gol
from gui.myqdialogs.AssessmentQDialog import AssessmentQDialog
from gui.mywidgets.MyQLable import MyQLabel
from gui.workQThead.UtilThread import CopyFileThread
from gui.workQThead.function_analysis.ClusterQThead import ClusterQThread
from util.Logger import logger


class KMeansWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.step = 1

    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(10)
        layout.setContentsMargins(20,20,10,10)

        vLayout1 = QVBoxLayout()
        vLayout1.setSpacing(10)

        label2 = QLabel("分析进展", self)
        self.resultEdit = QTextEdit(self)
        self.resultEdit.setReadOnly(True)
        self.resultEdit.append("基因共表达聚类分析及可视化：\n1. 样品少可以直接通过K-means进行聚类分析\n2. 样品多可以通过WGCNA进行聚类分析\n")

        vLayout1.addWidget(label2)
        vLayout1.addWidget(self.resultEdit)

        vLayout2 = QVBoxLayout()
        vLayout2.setSpacing(10)
        vLayout2.setAlignment(Qt.AlignTop)
        label3 = QLabel("数据导入（行为基因，列为样本）", self)
        label3.setStyleSheet("font-weight:bold")

        hLayout1 = QHBoxLayout()
        hLayout1.setSpacing(20)
        dataInputBtn = QPushButton(
            '表达数据', self, objectName='ClickBtn')
        dataInputBtn.setStyleSheet("background: #83c5be")
        dataInputBtn.clicked.connect(self.expression_data_import)
        label4 = MyQLabel("下载表达数据", self)
        label4.setStyleSheet("color:red;text-decoration:underline;")
        label4.connect_customized_slot(lambda: self.saveFile("expression_matrix.xlsx"))
        hLayout1.addWidget(dataInputBtn)
        hLayout1.addWidget(label4)
        hLayout1.addStretch(1)


        label6 = QLabel("设置分析流程中参数", self)
        label6.setStyleSheet("font-weight:bold")

        hLayout2 = QHBoxLayout()
        hLayout2.setSpacing(20)
        label5 = MyQLabel("1. 聚类维度：", self)
        self.clusterDim = QComboBox(self, minimumWidth=200)
        self.clusterDim.addItems(["列聚类（样本聚类）","行聚类（基因聚类）"])
        self.clusterDim.currentIndexChanged.connect(
                            lambda: self.cluster_dim_status(self.clusterDim.currentIndex()))
        hLayout2.addWidget(label5)
        hLayout2.addWidget(self.clusterDim)
        hLayout2.addStretch(1)

        hLayout6 = QHBoxLayout()
        hLayout6.setSpacing(10)
        self.label61 = QLabel("选择变异系数基因的百分比：",self)
        self.cvNum = QSpinBox()
        self.cvNum.setStyleSheet("min-width:100px")
        self.cvNum.setMinimum(10)
        self.cvNum.setMaximum(100)
        self.cvNum.setValue(20)
        self.label63 = QLabel("%", self)
        hLayout6.addWidget(self.label61)
        hLayout6.addWidget(self.cvNum)
        hLayout6.addWidget(self.label63)
        hLayout6.addStretch(1)
        self.label62 = QLabel("（选择变异系数高的部分基因）", self)


        hLayout71 = QHBoxLayout()
        hLayout71.setSpacing(10)
        label71 = QLabel("2. 聚类方法：",self)
        self.proteinColname = QComboBox(self, minimumWidth=200)
        self.proteinColname.addItems(["K-means"])
        # self.proteinColname.currentIndexChanged.connect(
        #     lambda: self.feature_select_change(self.proteinColname.currentIndex()))
        hLayout71.addWidget(label71)
        hLayout71.addWidget(self.proteinColname)
        hLayout71.addStretch(1)

        hLayout73 = QHBoxLayout()
        hLayout73.setSpacing(10)
        self.label73 = QLabel("3. 类的数目 ：", self)
        self.rb1 = QRadioButton('自动选择', self)
        self.rb2 = QRadioButton('自定义', self)
        self.bg1 = QButtonGroup(self)
        self.bg1.addButton(self.rb1, 11)
        self.bg1.addButton(self.rb2, 12)
        self.bg1.buttonClicked.connect(self.rbclicked)
        self.rb1.setChecked(True)
        hLayout73.addWidget(self.label73)
        hLayout73.addWidget(self.rb1)
        hLayout73.addWidget(self.rb2)
        hLayout73.addStretch(1)

        hLayout74 = QHBoxLayout()
        hLayout74.setSpacing(10)
        self.featureNum = QSpinBox()
        self.featureNum.setStyleSheet("min-width:120px")
        self.featureNum.setMinimum(2)
        self.featureNum.setVisible(False)
        self.featureNum.setValue(3)
        hLayout74.addWidget(self.featureNum)
        hLayout74.addStretch(1)

        label11 =  QLabel("结果导出", self)
        label11.setStyleSheet("font-weight:bold")

        hLayout7 = QHBoxLayout()
        hLayout7.setSpacing(10)
        label10 = QLabel("输出结果路径：",self)
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
        vLayout2.addWidget(label6)
        vLayout2.addLayout(hLayout2)
        vLayout2.addLayout(hLayout6)
        vLayout2.addWidget(self.label62)
        vLayout2.addLayout(hLayout71)
        # vLayout2.addLayout(hLayout72)
        vLayout2.addLayout(hLayout73)
        vLayout2.addLayout(hLayout74)
        vLayout2.addWidget(label11)
        vLayout2.addLayout(hLayout7)
        vLayout2.addWidget(certainBtn)

        layout.addLayout(vLayout1,stretch=6)
        layout.addLayout(vLayout2,stretch=4)

    def cluster_dim_status(self,tag):
        if tag==0:
            self.label61.setVisible(True)
            self.label62.setVisible(True)
            self.label63.setVisible(True)
            self.cvNum.setVisible(True)
        else:
            self.label61.setVisible(False)
            self.label62.setVisible(False)
            self.label63.setVisible(False)
            self.cvNum.setVisible(False)

    def save_result(self):
        '''
        设置保存结果位置
        '''
        directory = QFileDialog.getExistingDirectory(self, "file Path", "")
        if directory is not None and directory != "":
            gol.set_value("cluster_result_path", directory)
            self.resultEdit.append(str(self.step)+".结果路径："+ directory)
            self.step += 1

    def rbclicked(self):
        if self.bg1.checkedId() == 11:
            self.featureNum.setVisible(False)
        else:
            self.featureNum.setVisible(True)

    def expression_data_import(self):
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                                   "(*.txt *.csv *.xlsx *.xls *.tsv)")
        if fileName is not None and fileName!="":
            self.resultEdit.append(str(self.step)+".导入的表达数据："+fileName)
            self.step += 1
            gol.set_value("cluster_expression_path", fileName)

    def info_display(self,step,text):
        '''
        分析过程中的正常日志打印
        step:操作步骤
        text：当前步骤的运行结果
        '''
        self.resultEdit.append(step+" :" + text)

    def error_display(self,text):
        '''
        text:失败信息
        '''
        self.resultEdit.append("运行失败，错误原因："+text)
        QMessageBox.warning(self, "发生错误", text)

    def saveFile(self,exit_file_name):
        file_type = exit_file_name.split(".")[-1]
        to_file_path, ftype = QFileDialog.getSaveFileName(self, 'save file', exit_file_name, "*."+file_type)
        if to_file_path:
            ResourcePath = gol.get_value("ResourcePath")
            exit_file_path = os.path.join(ResourcePath, "file","function_analysis",exit_file_name)
            t = CopyFileThread(exit_file_path,to_file_path)  # 目标函数
            t.start()  # 启动线程

    def certain(self):
        if gol.get_value("cluster_expression_path") and gol.get_value("cluster_result_path"):
            if self.bg1.checkedId() == 11:
                # 聚类的数目采用软件自动选择
                gol.set_value("auto_cluster_class_num", True)
            else:
                gol.set_value("auto_cluster_class_num", False)
                class_num = self.featureNum.value()
                gol.set_value("cluster_class_num",class_num)

            cluster_dim_index = self.clusterDim.currentIndex()
            gol.set_value("cluster_dim_index", cluster_dim_index)
            if cluster_dim_index==0:
                cv_ratio = self.cvNum.value()
                gol.set_value("cluster_cv_ratio", cv_ratio)
            self.resultEdit.append(str(self.step) + ".数据分析中...")
            self.main_thread = ClusterQThread()
            self.main_thread.error_trigger.connect(self.error_display)
            self.main_thread.info_trigger.connect(self.info_display)
            self.main_thread.start()
        else:
            QMessageBox.warning(self, "提示", "请先导入表达数据和设置结果路径！")


