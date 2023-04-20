from math import isclose
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, \
    QTextEdit, QLabel, QPushButton, QComboBox, QSpinBox, QLineEdit, QMessageBox, QFileDialog, QDialog, \
    QScrollArea, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
import os
import util.Global as gol
from gui.myqdialogs.AssessmentQDialog import AssessmentQDialog
from gui.myqdialogs.ChoiceQDialog import ChoiceQDialog
from gui.mywidgets.MyQLable import MyQLabel
from gui.workQThead.UtilThread import CopyFileThread
from gui.workQThead.biomarker_analysis.BiomarkerLabelFreeQThread import BiomarkerLabelFreeQThread
from service.FlowChartService import biomarker_label_free_flowchart, scale_flowchart_png
from util.Logger import logger
from util.StringUtil import IsFloatNum


class BiomarkerLabelFreeWidget(QWidget):
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
        label1 = QLabel("数据分析流程", self)
        # 加载流程图
        ResourcePath = gol.get_value("ResourcePath")
        indexPath = os.path.join(ResourcePath, "img","flowchart","biomarker_label_free.png")
        pix = scale_flowchart_png(indexPath)
        self.item = QGraphicsPixmapItem(pix)  # 创建像素图元
        self.scene = QGraphicsScene()  # 创建场景
        self.scene.addItem(self.item)
        self.picshow = QGraphicsView()
        self.picshow.setScene(self.scene)  # 将场景添加至视图

        label2 = QLabel("分析进展", self)
        self.resultEdit = QTextEdit(self)
        self.resultEdit.setReadOnly(True)

        vLayout1.addWidget(label1)
        vLayout1.addWidget(self.picshow)
        vLayout1.addWidget(label2)
        vLayout1.addWidget(self.resultEdit)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()

        vLayout2 = QVBoxLayout()
        vLayout2.setSpacing(10)
        vLayout2.setAlignment(Qt.AlignTop)
        label3 =  QLabel("数据导入", self)
        label3.setStyleSheet("font-weight:bold")

        hLayout1 = QHBoxLayout()
        hLayout1.setSpacing(20)
        dataInputBtn = QPushButton(
            '表达数据', self, objectName='ClickBtn')
        dataInputBtn.setStyleSheet("background: #83c5be")
        dataInputBtn.clicked.connect(self.expression_data_import)
        label4 = MyQLabel("下载表达数据",self)
        label4.setStyleSheet("color:red;text-decoration:underline;")
        label4.connect_customized_slot(lambda: self.saveFile("label_free_pro_data.xlsx"))
        hLayout1.addWidget(dataInputBtn)
        hLayout1.addWidget(label4)
        hLayout1.addStretch(1)

        hLayout2 = QHBoxLayout()
        hLayout2.setSpacing(20)
        informationBtn = QPushButton(
            '样本信息表', self, objectName='ClickBtn')
        informationBtn.setStyleSheet("background: #83c5be")
        informationBtn.clicked.connect(self.information_data_import)
        label5 = MyQLabel("下载样本信息表",self)
        label5.setStyleSheet("color:red;text-decoration:underline;")
        label5.connect_customized_slot(lambda: self.saveFile("label_free_pro_sampleInformation.xlsx"))
        hLayout2.addWidget(informationBtn)
        hLayout2.addWidget(label5)
        hLayout2.addStretch(1)

        hLayout21 = QHBoxLayout()
        hLayout21.setSpacing(20)
        self.geneNameCol = QCheckBox()
        self.geneNameCol.setText("设置基因名称对应的列")
        # hLayout8.addWidget(label81)
        self.geneNameColBtn = QPushButton('基因名列', self, objectName='ClickBtn')
        self.geneNameColBtn.setStyleSheet("background: #83c5be;max-width: 120px;")
        self.geneNameColBtn.clicked.connect(self.set_col_name)
        self.geneNameColBtn.setVisible(False)

        self.geneNameCol.stateChanged.connect(lambda: self.geneNameState(self.geneNameCol))
        hLayout21.addWidget(self.geneNameCol)
        hLayout21.addWidget(self.geneNameColBtn)
        hLayout21.addStretch(1)

        label5a =  QLabel("设置阴性和阳性分析", self)
        label5a.setStyleSheet("font-weight:bold")

        groupBtn = QPushButton('选择分组', self, objectName='ClickBtn')
        groupBtn.setStyleSheet("background: #83c5be;max-width: 120px;")
        groupBtn.clicked.connect(self.choose_group)

        label6b =  QLabel("新的测试数据集", self)
        label6b.setStyleSheet("font-weight:bold")

        label6ba = QLabel("(新的测试数据集可导入也可不导入)", self)

        hLayout2a = QHBoxLayout()
        hLayout2a.setSpacing(20)
        testDataBtn = QPushButton(
            '新的测试数据集', self, objectName='ClickBtn')
        testDataBtn.setStyleSheet("background: #83c5be")
        testDataBtn.clicked.connect(self.test_data_import)
        label6ba0 = MyQLabel("清除", self)
        label6ba0.setStyleSheet("color:blue;text-decoration:underline;")
        label6ba0.connect_customized_slot(self.clear_test_data)
        label6ba1 = MyQLabel("下载新的测试数据集",self)
        label6ba1.setStyleSheet("color:red;text-decoration:underline;")
        label6ba1.connect_customized_slot(lambda: self.saveFile("label_free_pro_data.xlsx"))
        hLayout2a.addWidget(testDataBtn)
        hLayout2a.addWidget(label6ba0)
        hLayout2a.addWidget(label6ba1)
        hLayout2a.addStretch(1)

        hLayout3b = QHBoxLayout()
        hLayout3b.setSpacing(20)
        testInformationBtn = QPushButton(
            '样本信息表', self, objectName='ClickBtn')
        testInformationBtn.setStyleSheet("background: #83c5be")
        testInformationBtn.clicked.connect(self.test_information_import)
        label6ba2 = MyQLabel("下载测试数据集的样本信息表",self)
        label6ba2.setStyleSheet("color:red;text-decoration:underline;")
        label6ba2.connect_customized_slot(lambda: self.saveFile("label_free_pro_sampleInformation.xlsx"))
        hLayout3b.addWidget(testInformationBtn)
        hLayout3b.addWidget(label6ba2)
        hLayout3b.addStretch(1)

        hLayout31 = QHBoxLayout()
        hLayout31.setSpacing(20)
        self.newGeneNameCol = QCheckBox()
        self.newGeneNameCol.setText("设置基因名称对应的列")
        # hLayout8.addWidget(label81)
        self.newGeneNameColBtn = QPushButton('基因名列', self, objectName='ClickBtn')
        self.newGeneNameColBtn.setStyleSheet("background: #83c5be;max-width: 120px;")
        self.newGeneNameColBtn.clicked.connect(self.set_new_col_name)
        self.newGeneNameColBtn.setVisible(False)

        self.newGeneNameCol.stateChanged.connect(lambda: self.newGeneNameState(self.newGeneNameCol))
        hLayout31.addWidget(self.newGeneNameCol)
        hLayout31.addWidget(self.newGeneNameColBtn)
        hLayout31.addStretch(1)

        label6 =  QLabel("设置预处理流程中参数", self)
        label6.setStyleSheet("font-weight:bold")

        hLayout3 = QHBoxLayout()
        hLayout3.setSpacing(10)
        label7 = QLabel("1. 校正方法：",self)
        self.normMethod = QComboBox(self, minimumWidth=200)
        self.normMethod.addItems(["上四分位数校正","分位数校正","不校正","样本和的中位数校正","FOT校正"])
        hLayout3.addWidget(label7)
        hLayout3.addWidget(self.normMethod)
        hLayout3.addStretch(1)

        hLayoutb4 = QHBoxLayout()
        hLayoutb4.setSpacing(10)
        labelb8 = QLabel("2. 缺失值过滤：", self)
        self.choice_filter = QComboBox(self, minimumWidth=200)
        self.choice_filter.addItems(["按照非缺失值数量来过滤", "按照缺失值百分比来过滤"])
        self.choice_filter.currentIndexChanged.connect(
            lambda: self.choice_filter_select_change(self.choice_filter.currentIndex()))
        hLayoutb4.addWidget(labelb8)
        hLayoutb4.addWidget(self.choice_filter)
        hLayoutb4.addStretch(1)

        hLayout4 = QHBoxLayout()
        hLayout4.setSpacing(10)
        self.label8 = QLabel("各组中非缺失值样本数n低于：")
        self.cb1 = QSpinBox()
        self.cb1.setStyleSheet("min-width:120px")
        self.cb1.setMinimum(3)
        self.cb1.setValue(3)
        # self.cb1.valueChanged.connect(self.Valuechange)
        hLayout4.addWidget(self.label8)
        hLayout4.addWidget(self.cb1)
        hLayout4.addStretch(1)

        hLayouta4 = QHBoxLayout()
        hLayouta4.setSpacing(10)
        self.labela8 = QLabel("各组中缺失值样本数量占比高于：")
        self.acb1 = QSpinBox()
        self.acb1.setStyleSheet("min-width:120px")
        self.acb1.setMinimum(2)
        self.acb1.setMaximum(100)
        self.acb1.setValue(50)
        self.labelaa8 = QLabel("%")
        hLayouta4.addWidget(self.labela8)
        hLayouta4.addWidget(self.acb1)
        hLayouta4.addWidget(self.labelaa8)
        hLayouta4.addStretch(1)
        self.labela8.setVisible(False)
        self.acb1.setVisible(False)
        self.labelaa8.setVisible(False)

        hLayout5 = QHBoxLayout()
        hLayout5.setSpacing(10)
        label9 = QLabel("3. 缺失值填补：",self)
        self.imputationMethod = QComboBox(self, minimumWidth=200)
        self.imputationMethod.addItems(["最小值填补","K近邻填补","随机森林填补"])
        hLayout5.addWidget(label9)
        hLayout5.addWidget(self.imputationMethod)
        hLayout5.addStretch(1)

        label10 =  QLabel("设置数据集拆分比例", self)
        label10.setStyleSheet("font-weight:bold")

        label10n = QLabel("训练集、测试集、验证集比例和为1", self)

        hLayout6 = QHBoxLayout()
        hLayout6.setSpacing(10)
        label11 = QLabel("1. 训练集比例：",self)
        self.trainRatio = QLineEdit()
        # (0,1,2) 0~1,小数为后2为
        self.trainRatio.setValidator(QDoubleValidator(0,1,2))
        self.trainRatio.setStyleSheet("min-width:120px")
        self.trainRatio.setText("0.70")
        # self.cb1.valueChanged.connect(self.Valuechange)
        hLayout6.addWidget(label11)
        hLayout6.addWidget(self.trainRatio)
        hLayout6.addStretch(1)

        hLayout7 = QHBoxLayout()
        hLayout7.setSpacing(10)
        label12 = QLabel("3. 测试集比例：",self)
        self.testRatio = QLineEdit()
        # (0,1,2) 0~1,小数为后2为
        self.testRatio.setValidator(QDoubleValidator(0,1,2))
        self.testRatio.setStyleSheet("min-width:120px")
        self.testRatio.setText("0.30")
        hLayout7.addWidget(label12)
        hLayout7.addWidget(self.testRatio)
        hLayout7.addStretch(1)

        hLayout8 = QHBoxLayout()
        hLayout8.setSpacing(10)
        label13 = QLabel("2. 验证集比例：",self)
        self.verificationRatio = QLineEdit()
        # (0,1,2) 0~1,小数为后2为
        self.verificationRatio.setValidator(QDoubleValidator(0,1,2))
        self.verificationRatio.setStyleSheet("min-width:120px")
        self.verificationRatio.setText("0")
        # self.verificationRatio.setDisabled(True)
        hLayout8.addWidget(label13)
        hLayout8.addWidget(self.verificationRatio)
        hLayout8.addStretch(1)

        label14 =  QLabel("设置特征筛选的方法", self)
        label14.setStyleSheet("font-weight:bold")

        # label14a = QLabel("(基于模型的特征选择方法:lasso、Ridge、LinearRegression、RandomForest、RFE)", self)

        hLayout9 = QHBoxLayout()
        hLayout9.setSpacing(10)
        label15 = QLabel("1. 特征筛选的方法：",self)
        self.featureSelectMethod = QComboBox(self, minimumWidth=200)
        self.featureSelectMethod.addItems(["差异分析","差异分析+Lasso特征筛选","差异分析+随机森林特征筛选","差异分析+递归特征消除法","差异分析+岭回归特征筛选"])
        # self.featureSelectMethod.currentIndexChanged.connect(
        #                     lambda: self.feature_select_change(self.featureSelectMethod.currentIndex()))
        hLayout9.addWidget(label15)
        hLayout9.addWidget(self.featureSelectMethod)
        hLayout9.addStretch(1)

        hLayoutb10 = QHBoxLayout()
        hLayoutb10.setSpacing(10)
        labelb16 = QLabel("P值：",self)
        self.p_or_q = QComboBox(self, minimumWidth=200)
        self.p_or_q.addItems(["P值","校正后的P值"])
        hLayoutb10.addWidget(labelb16)
        hLayoutb10.addWidget(self.p_or_q)
        hLayoutb10.addStretch(1)

        hLayout10 = QHBoxLayout()
        hLayout10.setSpacing(10)
        self.label16 = QLabel("不高于：",self)
        self.pvalueEdit = QLineEdit(self)
        self.pvalueEdit.setText("0.05")
        self.pvalueEdit.setValidator(QDoubleValidator())
        hLayout10.addWidget(self.label16)
        hLayout10.addWidget(self.pvalueEdit)
        hLayout10.addStretch(1)

        hLayout11 = QHBoxLayout()
        hLayout11.setSpacing(10)
        self.label17 = QLabel("差异倍数FC的范围：",self)
        self.fcQComboBox = QComboBox(self, minimumWidth=200)
        self.fcQComboBox.addItems(["FC ≥ 1.5 或 FC ≤ 0.67","FC ≥ 1.25 或 FC ≤ 0.8","FC ≥ 2 或 FC ≤ 0.5","FC ≥ 4 或 FC ≤ 0.25"])
        hLayout11.addWidget(self.label17)
        hLayout11.addWidget(self.fcQComboBox)
        hLayout11.addStretch(1)

        hLayout11a = QHBoxLayout()
        hLayout11a.setSpacing(10)
        label17a = QLabel("2. 筛选后的特征数不多于：",self)
        self.featureNum = QSpinBox()
        self.featureNum.setStyleSheet("min-width:120px")
        self.featureNum.setMinimum(3)
        self.featureNum.setValue(20)
        # self.cb1.valueChanged.connect(self.Valuechange)
        hLayout11a.addWidget(label17a)
        hLayout11a.addWidget(self.featureNum)
        hLayout11a.addStretch(1)

        label18 =  QLabel("设置分类器算法", self)
        label18.setStyleSheet("font-weight:bold")

        hLayout12 = QHBoxLayout()
        hLayout12.setSpacing(10)
        label19 = QLabel("1. 分类器算法：",self)
        self.classifierMethod = QComboBox(self, minimumWidth=200)
        self.classifierMethod.addItems(["随机森林","非线性SVM","朴素贝叶斯","逻辑回归","随机梯度下降分类","以上所有"])
        hLayout12.addWidget(label19)
        hLayout12.addWidget(self.classifierMethod)
        hLayout12.addStretch(1)

        label20 =  QLabel("结果导出", self)
        label20.setStyleSheet("font-weight:bold")

        hLayout13 = QHBoxLayout()
        hLayout13.setSpacing(10)
        label21 = QLabel("输出结果路径：",self)
        self.saveFileBtn = QPushButton('路径选择', self, objectName='ClickBtn')
        self.saveFileBtn.setStyleSheet("background: #83c5be")
        self.saveFileBtn.clicked.connect(self.save_result)
        hLayout13.addWidget(label21)
        hLayout13.addWidget(self.saveFileBtn)
        hLayout13.addStretch(1)

        certainBtn = QPushButton('确定', self, objectName='ClickBtn')
        certainBtn.setStyleSheet("background: #83c5be;max-width: 120px;")
        certainBtn.clicked.connect(self.certain)

        vLayout2.addWidget(label3)
        vLayout2.addLayout(hLayout1)
        vLayout2.addLayout(hLayout2)
        vLayout2.addLayout(hLayout21)

        vLayout2.addWidget(label6b)
        vLayout2.addWidget(label6ba)
        vLayout2.addLayout(hLayout2a)
        vLayout2.addLayout(hLayout3b)
        vLayout2.addLayout(hLayout31)

        vLayout2.addWidget(label5a)
        vLayout2.addWidget(groupBtn)

        vLayout2.addWidget(label6)
        vLayout2.addLayout(hLayout3)
        vLayout2.addLayout(hLayoutb4)
        vLayout2.addLayout(hLayout4)
        vLayout2.addLayout(hLayouta4)
        vLayout2.addLayout(hLayout5)

        vLayout2.addWidget(label10)
        vLayout2.addWidget(label10n)
        vLayout2.addLayout(hLayout6)
        vLayout2.addLayout(hLayout8)
        vLayout2.addLayout(hLayout7)


        vLayout2.addWidget(label14)
        # vLayout2.addWidget(label14a)
        vLayout2.addLayout(hLayout9)
        vLayout2.addLayout(hLayoutb10)
        vLayout2.addLayout(hLayout10)
        vLayout2.addLayout(hLayout11)
        vLayout2.addLayout(hLayout11a)

        vLayout2.addWidget(label18)
        vLayout2.addLayout(hLayout12)

        vLayout2.addWidget(label20)
        vLayout2.addLayout(hLayout13)
        vLayout2.addWidget(certainBtn)

        self.scrollAreaWidgetContents.setLayout(vLayout2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        layout.addLayout(vLayout1,stretch=6)
        # layout.addLayout(vLayout2,stretch=4)
        layout.addWidget(self.scrollArea,stretch=4)

    def geneNameState(self, cb):
        if self.geneNameCol.isChecked():
            self.geneNameColBtn.setVisible(True)
        else:
            self.geneNameColBtn.setVisible(False)

    def newGeneNameState(self, cb):
        if self.newGeneNameCol.isChecked():
            self.newGeneNameColBtn.setVisible(True)
        else:
            self.newGeneNameColBtn.setVisible(False)

    def set_col_name(self):
        biomarker_label_free_expression_path = gol.get_value("biomarker_label_free_expression_path")
        if biomarker_label_free_expression_path:
            try:
                choiceQDialog = ChoiceQDialog()
                choiceQDialog.initUI(self.resultEdit, "biomarker_label_free_gene_name", "基因名称对应的列", biomarker_label_free_expression_path)
                if choiceQDialog.exec_() == QDialog.Accepted:
                    pass
            except Exception as e:
                logger.error(e)
                logger.error(f"参数biomarker_label_free_expression_path：{biomarker_label_free_expression_path}")

    def set_new_col_name(self):
        biomarker_label_free_test_expression_path = gol.get_value("biomarker_label_free_test_data_path")
        if biomarker_label_free_test_expression_path:
            try:
                choiceQDialog = ChoiceQDialog()
                choiceQDialog.initUI(self.resultEdit, "biomarker_label_free_test_gene_name", "基因名称对应的列", biomarker_label_free_test_expression_path)
                if choiceQDialog.exec_() == QDialog.Accepted:
                    pass
            except Exception as e:
                logger.error(e)
                logger.error(f"参数biomarker_label_free_test_expression_path：{biomarker_label_free_test_expression_path}")

    def choice_filter_select_change(self,tag):
        # 选择不同的过滤规则时出现不同的过滤条件
        if tag==0:
            self.label8.setVisible(True)
            self.cb1.setVisible(True)
            self.labela8.setVisible(False)
            self.acb1.setVisible(False)
            self.labelaa8.setVisible(False)
        else:
            self.label8.setVisible(False)
            self.cb1.setVisible(False)
            self.labela8.setVisible(True)
            self.acb1.setVisible(True)
            self.labelaa8.setVisible(True)

    def expression_data_import(self):
        '''
        导入表达数据文件
        '''
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                         "(*.txt *.csv *.xlsx *.xls *.tsv)")
        if fileName is not None and fileName != "":
            self.resultEdit.append(str(self.step) + ".表达数据文件：" + fileName)
            self.step += 1
            gol.set_value("biomarker_label_free_expression_path", fileName)

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
            exit_file_path = os.path.join(ResourcePath, "file","label_free_pro",exit_file_name)
            t = CopyFileThread(exit_file_path,to_file_path)  # 目标函数
            t.start()  # 启动线程

    def certain(self):
        # 查看三个比例相加是否是1
        train_ratio = float(self.trainRatio.text())
        test_ratio = float(self.testRatio.text())
        verification_ratio = float(self.verificationRatio.text())
        if not isclose(1, train_ratio+test_ratio+verification_ratio, rel_tol=1e-5):
            QMessageBox.warning(self, "提示", "数据集拆分比例不正确！")
            return None
        # 校正
        norm = self.normMethod.currentText()
        norm_index = self.normMethod.currentIndex()
        # 缺失值过滤
        choice_filter_index = self.choice_filter.currentIndex()
        miss_n = self.cb1.value()
        miss_ratio = self.acb1.value()
        gol.set_value("biomarker_label_free_miss_n",miss_n)
        gol.set_value("biomarker_label_free_miss_ratio",miss_ratio)
        gol.set_value("biomarker_label_free_filter_index",choice_filter_index)

        # 缺失值填补
        imputation = self.imputationMethod.currentText()
        imputation_index = self.imputationMethod.currentIndex()

        # 特征筛选
        feature_select = self.featureSelectMethod.currentText()
        feature_select_index = self.featureSelectMethod.currentIndex()

        # P值
        # p值 or FDR
        p_threshold_index = self.p_or_q.currentIndex()
        pvalue = self.pvalueEdit.text()
        if not IsFloatNum(pvalue):
            QMessageBox.warning(self, "提示", "p值不正确！")
            return None
        gol.set_value("biomarker_label_free_p", pvalue)
        gol.set_value("biomarker_label_free_p_threshold_index", p_threshold_index)

        fc = self.fcQComboBox.currentText()
        fc_index = self.fcQComboBox.currentIndex()
        gol.set_value("biomarker_label_free_fc", fc)
        gol.set_value("biomarker_label_free_fc_index", fc_index)

        max_feature_num = self.featureNum.value()
        classifier = self.classifierMethod.currentText()
        classifier_index = self.classifierMethod.currentIndex()
        gol.set_value("biomarker_label_free_norm",norm)
        gol.set_value("biomarker_label_free_norm_index",norm_index)
        gol.set_value("biomarker_label_free_imputation",imputation)
        gol.set_value("biomarker_label_free_imputation_index",imputation_index)
        gol.set_value("biomarker_label_free_feature_select",feature_select)
        gol.set_value("biomarker_label_free_feature_select_index",feature_select_index)
        gol.set_value("biomarker_label_free_max_feature_num",max_feature_num)
        gol.set_value("biomarker_label_free_classifier",classifier)
        gol.set_value("biomarker_label_free_classifier_index",classifier_index)
        gol.set_value("biomarker_label_free_train_ratio",train_ratio)
        gol.set_value("biomarker_label_free_test_ratio",test_ratio)
        gol.set_value("biomarker_label_free_verification_ratio",verification_ratio)
        # 基因名称列
        if_gene_name = self.geneNameCol.isChecked()
        gol.set_value("biomarker_label_free_if_gene_name", if_gene_name)
        if if_gene_name:
            if not gol.get_value("biomarker_label_free_gene_name"):
                QMessageBox.warning(self, "基因名称列", "请设置基因名称对应的列")
                return
        test_if_gene_name = self.newGeneNameCol.isChecked()
        gol.set_value("biomarker_label_free_test_if_gene_name", test_if_gene_name)
        if test_if_gene_name:
            if not gol.get_value("biomarker_label_free_test_gene_name"):
                QMessageBox.warning(self, "基因名称列", "请设置基因名称对应的列")
                return
        # 更新流程图，没有新建线程
        try:
            flowchart_path = biomarker_label_free_flowchart()
            self.item.setPixmap(scale_flowchart_png(flowchart_path))
            self.resultEdit.append(str(self.step) + ".更新流程图成功！")
            self.step += 1
        except Exception as e:
            logger.error("更新流程图失败",e)
            QMessageBox.warning(self, "更新流程图失败", "graphviz软件未安装成功")
        self.resultEdit.append(str(self.step) + ".数据分析中...")
        self.main_thread = BiomarkerLabelFreeQThread()
        self.main_thread.error_trigger.connect(self.error_display)
        self.main_thread.info_trigger.connect(self.info_display)
        self.main_thread.start()

    def save_result(self):
        '''
        设置保存结果位置
        '''
        directory = QFileDialog.getExistingDirectory(self, "file Path", "")
        if directory is not None and directory != "":
            gol.set_value("biomarker_label_free_result_path", directory)
            self.resultEdit.append(str(self.step)+".结果路径："+ directory)
            self.step += 1

    def choose_group(self):
        '''
        设置分组信息
        '''
        biomarker_label_free_information_path = gol.get_value("biomarker_label_free_information_path")
        if biomarker_label_free_information_path:
            try:
                assessmentQDialog = AssessmentQDialog()
                assessmentQDialog.initUI(self.resultEdit,"biomarker_label_free",2)
                if assessmentQDialog.exec_() == QDialog.Accepted:
                    pass
            except Exception as e:
                logger.error(e)

    def information_data_import(self):
        '''
        导入样本信息文件
        '''
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                                   "(*.txt *.csv *.xlsx *.xls *.tsv)")
        if fileName is not None and fileName!="":
            self.resultEdit.append(str(self.step)+".样本信息表："+fileName)
            self.step +=1
            gol.set_value("biomarker_label_free_information_path", fileName)

    def test_information_import(self):
        '''
        导入测试数据集的样本信息文件
        '''
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                                   "(*.txt *.csv *.xlsx *.xls *.tsv)")
        if fileName is not None and fileName!="":
            self.resultEdit.append(str(self.step)+".新的测试数据集的样本信息表："+fileName)
            self.step +=1
            gol.set_value("biomarker_label_free_test_information_path", fileName)

    def test_data_import(self):
        '''
        导入测试数据集
        '''
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                                   "(*.txt *.csv *.xlsx *.xls *.tsv)")
        if fileName is not None and fileName!="":
            self.resultEdit.append(str(self.step)+".新的测试数据："+fileName)
            self.step +=1
            gol.set_value("biomarker_label_free_test_data_path", fileName)
            self.testRatio.setText("0")
            self.testRatio.setDisabled(True)

    def clear_test_data(self):
        fileName = gol.remove_value("biomarker_label_free_test_data_path")
        if len(fileName)>0:
            self.resultEdit.append(".删除新的测试数据集：" + fileName)
        self.testRatio.setDisabled(False)

