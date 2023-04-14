from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
    QTextEdit, QLabel, QPushButton, QMessageBox, QFileDialog, QDialog, \
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsView
from PyQt5.QtCore import Qt
import os
import util.Global as gol
from gui.myqdialogs.ChoiceQDialog import ChoiceQDialog
from gui.mywidgets.MyQLable import MyQLabel
from gui.workQThead.UtilThread import CopyFileThread
from gui.workQThead.function_analysis.WgcnaQThead import WGCNAQThread
from service.FlowChartService import scale_flowchart_png
from util.Logger import logger


class WGCNAWidget(QWidget):
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
        indexPath = os.path.join(ResourcePath, "img","flowchart","wgcna.png")
        pix = scale_flowchart_png(indexPath)
        self.item = QGraphicsPixmapItem(pix)  # 创建像素图元
        self.scene = QGraphicsScene()  # 创建场景
        self.scene.addItem(self.item)
        self.picshow = QGraphicsView()
        self.picshow.setScene(self.scene)  # 将场景添加至视图

        label2 = QLabel("分析进展", self)
        self.resultEdit = QTextEdit(self)
        self.resultEdit.setReadOnly(True)
        self.resultEdit.append("介绍：加权基因共表达网络分析 (WGCNA, Weighted correlation networkanalysis)是用来描述不同样品之间基因关联模式的系统生物学方法，可以用来鉴定高度协同变化的基因集,并根据基因集的内连性和基因集与表型之间的关联鉴定候补生物标记基因或治疗靶点。相比于只关注差异表达的基因，WGCNA利用数千或近万个变化最大的基因或全部基因的信息识别感兴趣的基因集，并与表型进行显著性关联分析。一是充分利用了信息，二是把数千个基因与表型的关联转换为数个基因集与表型的关联，免去了多重假设检验校正的问题。\n表达数据：数据样本量最少为20个，样本太少无法聚类；表达数据应为FPKM形式，因为FPKM数据满足了样本间和样本内的校正；表达数据行为基因，列为样本。\n表型数据：要求是数值化的数据，且样本名称为第一列。\n\n")

        vLayout1.addWidget(label1)
        vLayout1.addWidget(self.picshow)
        vLayout1.addWidget(label2)
        vLayout1.addWidget(self.resultEdit)

        vLayout2 = QVBoxLayout()
        vLayout2.setSpacing(10)
        vLayout2.setAlignment(Qt.AlignTop)
        label3 = QLabel("数据导入", self)
        label3.setStyleSheet("font-weight:bold")

        hLayout1 = QHBoxLayout()
        hLayout1.setSpacing(20)
        dataInputBtn = QPushButton(
            '表达数据', self, objectName='ClickBtn')
        dataInputBtn.setStyleSheet("background: #83c5be")
        dataInputBtn.clicked.connect(self.expression_data_import)
        label4 = MyQLabel("下载表达数据", self)
        label4.setStyleSheet("color:red;text-decoration:underline;")
        label4.connect_customized_slot(lambda: self.saveFile("wgcna_expression.xlsx"))
        hLayout1.addWidget(dataInputBtn)
        hLayout1.addWidget(label4)
        hLayout1.addStretch(1)

        hLayout2 = QHBoxLayout()
        hLayout2.setSpacing(20)
        informationBtn = QPushButton(
            '表型数据', self, objectName='ClickBtn')
        informationBtn.setStyleSheet("background: #83c5be")
        informationBtn.clicked.connect(self.information_data_import)
        label5 = MyQLabel("下载表型数据", self)
        label5.setStyleSheet("color:red;text-decoration:underline;")
        label5.connect_customized_slot(lambda: self.saveFile("wgcna_traits.xlsx"))
        hLayout2.addWidget(informationBtn)
        hLayout2.addWidget(label5)
        hLayout2.addStretch(1)

        label12 = QLabel("选择感兴趣的表型", self)
        label12.setStyleSheet("font-weight:bold")

        groupBtn = QPushButton('选择表型', self, objectName='ClickBtn')
        groupBtn.setStyleSheet("background: #83c5be;max-width: 120px;")
        groupBtn.clicked.connect(self.choose_trait)

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
        vLayout2.addLayout(hLayout2)
        vLayout2.addWidget(label12)
        vLayout2.addWidget(groupBtn)
        vLayout2.addWidget(label11)
        vLayout2.addLayout(hLayout7)
        vLayout2.addWidget(certainBtn)

        layout.addLayout(vLayout1,stretch=6)
        layout.addLayout(vLayout2,stretch=4)

    def save_result(self):
        '''
        设置保存结果位置
        '''
        directory = QFileDialog.getExistingDirectory(self, "file Path", "")
        if directory is not None and directory != "":
            gol.set_value("wgcna_result_path", directory)
            self.resultEdit.append(str(self.step)+".结果路径："+ directory)
            self.step += 1

    def expression_data_import(self):
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                                   "(*.txt *.csv *.xlsx *.xls *.tsv)")
        if fileName is not None and fileName!="":
            self.resultEdit.append(str(self.step)+".导入的表达数据："+fileName)
            self.step += 1
            gol.set_value("wgcna_expression_path", fileName)

    def information_data_import(self):
        '''
        导入样本信息文件
        '''
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                                   "(*.txt *.csv *.xlsx *.xls *.tsv)")
        if fileName is not None and fileName!="":
            self.resultEdit.append(str(self.step)+".导入的表型数据："+fileName)
            self.step +=1
            gol.set_value("wgcna_information_path", fileName)

    def choose_trait(self):
        '''
        选择最感兴趣的表型特征
        '''
        wgcna_information_path = gol.get_value("wgcna_information_path")
        if wgcna_information_path:
            try:
                choiceQDialog = ChoiceQDialog()
                choiceQDialog.initUI(self.resultEdit, "wgcna_interested_trait", "选择最感兴趣的表型特征", wgcna_information_path)
                if choiceQDialog.exec_() == QDialog.Accepted:
                    pass
            except Exception as e:
                logger.error(e)
        else:
            QMessageBox.warning(self, "数据未导入", "请先导入表型数据")

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
        if gol.get_value("wgcna_interested_trait") and gol.get_value("wgcna_information_path") and gol.get_value("wgcna_expression_path") and gol.get_value("wgcna_result_path"):
            self.resultEdit.append(str(self.step) + ".数据分析中...")
            self.main_thread = WGCNAQThread()
            self.main_thread.error_trigger.connect(self.error_display)
            self.main_thread.info_trigger.connect(self.info_display)
            self.main_thread.start()
        else:
            QMessageBox.warning(self, "提示", "请先导入数据和设置参数！")


