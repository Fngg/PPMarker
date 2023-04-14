from PyQt5.QtGui import QPixmap, QDoubleValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, \
    QTextEdit, QLabel, QPushButton, QComboBox, QSpinBox, QLineEdit, QMessageBox, QFileDialog, QDialog, QRadioButton, \
    QCheckBox
from PyQt5.QtCore import Qt
import os
import util.Global as gol
from gui.myqdialogs.AssessmentQDialog import AssessmentQDialog
from gui.mywidgets.MyQLable import MyQLabel
from gui.workQThead.difference_analysis.LabelFreePhoQThread import LabelFreePhoQThread
from util.StringUtil import IsFloatNum
from service.FlowChartService import label_free_pho_flowchart, scale_flowchart_png


class LabelFreePhoWidget(QWidget):
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
        indexPath = os.path.join(ResourcePath, "img","flowchart","label_free_pho.png")
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
        hLayout2.addWidget(informationBtn)
        hLayout2.addWidget(label5)
        hLayout2.addStretch(1)

        hLayout8 = QHBoxLayout()
        hLayout8.setSpacing(20)
        proBtn = QPushButton(
            '蛋白组差异表达结果', self, objectName='ClickBtn')
        proBtn.setStyleSheet("background: #83c5be")
        proBtn.clicked.connect(self.pro_data_import)
        label81 = MyQLabel("下载蛋白组差异表达结果",self)
        label81.setStyleSheet("color:red;text-decoration:underline;")
        hLayout8.addWidget(proBtn)
        hLayout8.addWidget(label81)
        hLayout8.addStretch(1)

        label12 =  QLabel("设置阴性和阳性分析", self)
        label12.setStyleSheet("font-weight:bold")

        groupBtn = QPushButton('选择分组', self, objectName='ClickBtn')
        groupBtn.setStyleSheet("background: #83c5be;max-width: 120px;")
        groupBtn.clicked.connect(self.choose_group)

        label6 =  QLabel("设置分析流程中参数", self)
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

        hLayout_fill = QHBoxLayout()
        hLayout_fill.setSpacing(10)
        label_fill = QLabel("3. 缺失值填补：", self)
        self.choice_fill = QComboBox(self, minimumWidth=200)
        self.choice_fill.addItems(["不填补", "最小值填补", "K近邻填补", "随机森林填补"])
        hLayout_fill.addWidget(label_fill)
        hLayout_fill.addWidget(self.choice_fill)
        hLayout_fill.addStretch(1)

        hLayoutb5 = QHBoxLayout()
        hLayoutb5.setSpacing(10)
        labelb9 = QLabel("4. P值：", self)
        self.p_or_q = QComboBox(self, minimumWidth=200)
        self.p_or_q.addItems(["P值", "校正后的P值"])
        hLayoutb5.addWidget(labelb9)
        hLayoutb5.addWidget(self.p_or_q)
        hLayoutb5.addStretch(1)

        hLayout5 = QHBoxLayout()
        hLayout5.setSpacing(10)
        label9 = QLabel("不高于：", self)
        self.pvalueEdit = QLineEdit(self)
        self.pvalueEdit.setText("0.05")
        self.pvalueEdit.setValidator(QDoubleValidator())
        hLayout5.addWidget(label9)
        hLayout5.addWidget(self.pvalueEdit)
        hLayout5.addStretch(1)

        hLayout6 = QHBoxLayout()
        hLayout6.setSpacing(10)
        label10 = QLabel("5. 差异倍数FC的范围：",self)
        self.fcQComboBox = QComboBox(self, minimumWidth=200)
        self.fcQComboBox.addItems(["FC ≥ 1.5 或 FC ≤ 0.67","FC ≥ 1.25 或 FC ≤ 0.8","FC ≥ 2 或 FC ≤ 0.5","FC ≥ 3 或 FC ≤ 0.33","FC ≥ 4 或 FC ≤ 0.25"])
        hLayout6.addWidget(label10)
        hLayout6.addWidget(self.fcQComboBox)
        hLayout6.addStretch(1)

        ## 富集分析参数
        hLayout9 = QHBoxLayout()
        hLayout9.setSpacing(20)
        self.cb_enrich = QCheckBox()
        self.cb_enrich.setText("是否进行富集分析")
        self.cb_enrich.stateChanged.connect(lambda: self.enrich_status(self.cb_enrich))
        hLayout9.addWidget(self.cb_enrich)
        hLayout9.addStretch(1)

        hLayout71 = QHBoxLayout()
        hLayout71.setSpacing(10)
        self.label71 = QLabel("6. 物种：", self)
        self.oriQComboBox = QComboBox(self, minimumWidth=200)
        self.oriQComboBox.addItems(["Homo Sapiens(9606)", "Mus Musculus(10090)"])
        hLayout71.addWidget(self.label71)
        hLayout71.addWidget(self.oriQComboBox)
        hLayout71.addStretch(1)

        hLayout72 = QHBoxLayout()
        hLayout72.setSpacing(10)
        self.label72 = QLabel("7. Gene names列格式：", self)
        self.geneTypeColname = QComboBox(self, minimumWidth=200)
        self.geneTypeColname.addItems(["Symbol", "Entrez ID", "Ensembl gene ID"])
        hLayout72.addWidget(self.label72)
        hLayout72.addWidget(self.geneTypeColname)
        hLayout72.addStretch(1)
        self.label72.setVisible(False)
        self.label71.setVisible(False)
        self.oriQComboBox.setVisible(False)
        self.geneTypeColname.setVisible(False)

        certainBtn = QPushButton('确定', self, objectName='ClickBtn')
        certainBtn.setStyleSheet("background: #83c5be;max-width: 120px;")
        certainBtn.clicked.connect(self.certain)

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


        vLayout2.addWidget(label3)
        vLayout2.addLayout(hLayout1)
        vLayout2.addLayout(hLayout2)
        vLayout2.addLayout(hLayout8)

        vLayout2.addWidget(label12)
        vLayout2.addWidget(groupBtn)

        vLayout2.addWidget(label6)
        vLayout2.addLayout(hLayout3)
        vLayout2.addLayout(hLayoutb4)
        vLayout2.addLayout(hLayout4)
        vLayout2.addLayout(hLayouta4)
        vLayout2.addLayout(hLayout_fill)
        vLayout2.addLayout(hLayoutb5)
        vLayout2.addLayout(hLayout5)
        vLayout2.addLayout(hLayout6)
        vLayout2.addLayout(hLayout9)
        vLayout2.addLayout(hLayout71)
        vLayout2.addLayout(hLayout72)
        vLayout2.addWidget(label11)
        vLayout2.addLayout(hLayout7)
        vLayout2.addWidget(certainBtn)

        layout.addLayout(vLayout1,stretch=6)
        layout.addLayout(vLayout2,stretch=4)

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

    def enrich_status(self,cb):
        if self.cb_enrich.isChecked():
            self.label72.setVisible(True)
            self.label71.setVisible(True)
            self.oriQComboBox.setVisible(True)
            self.geneTypeColname.setVisible(True)
        else:
            self.label72.setVisible(False)
            self.label71.setVisible(False)
            self.oriQComboBox.setVisible(False)
            self.geneTypeColname.setVisible(False)

    def certain(self):
        # 校正
        norm = self.normMethod.currentText()
        norm_index = self.normMethod.currentIndex()
        gol.set_value("label_free_pho_norm", norm)
        gol.set_value("label_free_pho_norm_index", norm_index)
        # 缺失值过滤
        choice_filter_index = self.choice_filter.currentIndex()
        miss_n = self.cb1.value()
        miss_ratio = self.acb1.value()
        gol.set_value("label_free_pho_miss_n", miss_n)
        gol.set_value("label_free_pho_miss_ratio", miss_ratio)
        gol.set_value("label_free_pho_filter_index", choice_filter_index)
        # 缺失值填补
        choice_fill_index = self.choice_fill.currentIndex()
        choice_fill_text = self.choice_fill.currentText()
        gol.set_value("label_free_pho_fill_index", choice_fill_index)
        gol.set_value("label_free_pho_fill_text", choice_fill_text)
        # p值 or FDR
        p_threshold_index = self.p_or_q.currentIndex()
        pvalue = self.pvalueEdit.text()
        if not IsFloatNum(pvalue):
            QMessageBox.warning(self, "提示", "p值不正确！")
            return None
        gol.set_value("label_free_pho_p", pvalue)
        gol.set_value("label_free_pho_p_threshold_index", p_threshold_index)
        # FC
        fc = self.fcQComboBox.currentText()
        fc_index = self.fcQComboBox.currentIndex()
        gol.set_value("label_free_pho_fc", fc)
        gol.set_value("label_free_pho_fc_index", fc_index)
        # 富集分析参数
        if_enrich = self.cb_enrich.isChecked()
        gol.set_value("label_free_pho_if_enrich", if_enrich)
        if if_enrich:
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
            gol.set_value("label_free_pho_org_type", enrichOrgType)
            gol.set_value("label_free_pho_gene_type", enrichGeneType)
        # 更新流程图，没有新建线程
        flowchart_path = label_free_pho_flowchart()
        self.item.setPixmap(scale_flowchart_png(flowchart_path))
        self.resultEdit.append(str(self.step) + ".更新流程图成功！")
        self.step += 1
        self.resultEdit.append(str(self.step) + ".数据分析中...")
        self.main_thread = LabelFreePhoQThread()
        self.main_thread.error_trigger.connect(self.error_display)
        self.main_thread.info_trigger.connect(self.info_display)
        self.main_thread.start()

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

    def expression_data_import(self):
        '''
        导入表达数据文件
        '''
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                                   "(*.txt *.csv *.xlsx *.xls *.tsv)")
        if fileName is not None and fileName!="":
            self.resultEdit.append(str(self.step)+".表达数据文件："+fileName)
            self.step += 1
            gol.set_value("label_free_pho_expression_path", fileName)

    def pro_data_import(self):
        '''
        导入蛋白质组差异表达结果
        '''
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                                   "(*.txt *.csv *.xlsx *.xls *.tsv)")
        if fileName is not None and fileName!="":
            self.resultEdit.append(str(self.step)+".蛋白质组差异表达结果："+fileName)
            self.step +=1
            gol.set_value("label_free_pho_prodata_path", fileName)

    def information_data_import(self):
        '''
        导入样本信息文件
        '''
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                                   "(*.txt *.csv *.xlsx *.xls *.tsv)")
        if fileName is not None and fileName!="":
            self.resultEdit.append(str(self.step)+".样本信息表："+fileName)
            self.step +=1
            gol.set_value("label_free_pho_information_path", fileName)

    def choose_group(self):
        '''
        设置分组信息
        '''
        label_free_pho_information_path = gol.get_value("label_free_pho_information_path")
        if label_free_pho_information_path:
            try:
                assessmentQDialog = AssessmentQDialog()
                assessmentQDialog.initUI(self.resultEdit,"label_free_pho",2)
                if assessmentQDialog.exec_() == QDialog.Accepted:
                    pass
            except Exception as e:
                print(e)

    def save_result(self):
        '''
        设置保存结果位置
        '''
        directory = QFileDialog.getExistingDirectory(self, "file Path", "")
        if directory is not None and directory != "":
            gol.set_value("label_free_pho_result_path", directory)
            self.resultEdit.append(str(self.step)+".结果路径："+ directory)
            self.step += 1









