from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QButtonGroup, \
    QTextEdit, QLabel, QPushButton, QComboBox, QMessageBox, QFileDialog, QRadioButton
from PyQt5.QtCore import Qt
import os
import util.Global as gol
from gui.mywidgets.MyQLable import MyQLabel
from gui.workQThead.UtilThread import CopyFileThread
from gui.workQThead.dia_analysis.DIAQThread import DIAQThread


class DIAWidget(QWidget):
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
        self.resultEdit.append("DIA数据处理介绍：\n支持DIA-NN软件，针对DIA-NN软件的结果数据进行处理，输出两个文件：以蛋白为行，样本为列的文件；以'Precursor.Id'为行，样本为列的文件。\n"+
                               "导入的文件必须有的列为：'File.Name','Protein.Names/Protein.Group','Precursor.Id','Precursor.Normalised'\n")

        vLayout1.addWidget(label2)
        vLayout1.addWidget(self.resultEdit)

        vLayout2 = QVBoxLayout()
        vLayout2.setSpacing(10)
        vLayout2.setAlignment(Qt.AlignTop)
        label3 =  QLabel("表达数据导入", self)
        label3.setStyleSheet("font-weight:bold")

        hLayout1 = QHBoxLayout()
        hLayout1.setSpacing(20)
        dataInputBtn = QPushButton(
            'DIANN的结果数据', self, objectName='ClickBtn')
        dataInputBtn.setStyleSheet("background: #83c5be")
        dataInputBtn.clicked.connect(self.expression_data_import)
        label4 = MyQLabel("下载DIANN的结果数据",self)
        label4.setStyleSheet("color:red;text-decoration:underline;")
        label4.connect_customized_slot(lambda: self.saveFile("diann_result.xlsx"))
        hLayout1.addWidget(dataInputBtn)
        hLayout1.addWidget(label4)
        hLayout1.addStretch(1)

        label31 =  QLabel("File.Name对应的样本名称", self)
        label31.setStyleSheet("font-weight:bold")

        hLayout2 = QHBoxLayout()
        hLayout2.setSpacing(20)
        self.rb1 = QRadioButton('无对应名称', self)
        self.rb2 = QRadioButton('有对应名称', self)
        self.bg1 = QButtonGroup(self)
        self.bg1.addButton(self.rb1, 11)
        self.bg1.addButton(self.rb2, 12)
        self.bg1.buttonClicked.connect(self.rbclicked)
        self.rb1.setChecked(True)
        hLayout2.addWidget(self.rb1)
        hLayout2.addWidget(self.rb2)
        hLayout2.addStretch(1)

        hLayout3= QHBoxLayout()
        hLayout3.setSpacing(20)
        self.simpleNameBtn = QPushButton(
            'File.Name对应的样本名称', self, objectName='ClickBtn')
        self.simpleNameBtn.setStyleSheet("background: #83c5be")
        self.simpleNameBtn.setDisabled(True)
        self.simpleNameBtn.clicked.connect(self.simple_name_import)
        label51 = MyQLabel("下载File.Name对应的样本名称",self)
        label51.setStyleSheet("color:red;text-decoration:underline;")
        label51.connect_customized_slot(lambda: self.saveFile("diann_simple.xlsx"))
        hLayout3.addWidget(self.simpleNameBtn)
        hLayout3.addWidget(label51)
        hLayout3.addStretch(1)

        label61 =  QLabel("设置参数", self)
        label61.setStyleSheet("font-weight:bold")

        hLayout71 = QHBoxLayout()
        hLayout71.setSpacing(10)
        label71 = QLabel("选择蛋白名称列：",self)
        self.proteinColname = QComboBox(self, minimumWidth=200)
        self.proteinColname.addItems(["Protein.Group","Protein.Names"])
        hLayout71.addWidget(label71)
        hLayout71.addWidget(self.proteinColname)
        hLayout71.addStretch(1)


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
        vLayout2.addWidget(label31)
        vLayout2.addLayout(hLayout2)
        vLayout2.addLayout(hLayout3)
        vLayout2.addWidget(label61)
        vLayout2.addLayout(hLayout71)
        vLayout2.addWidget(label11)
        vLayout2.addLayout(hLayout7)
        vLayout2.addWidget(certainBtn)

        layout.addLayout(vLayout1,stretch=6)
        layout.addLayout(vLayout2,stretch=4)

    def saveFile(self,exit_file_name):
        file_type = exit_file_name.split(".")[-1]
        to_file_path, ftype = QFileDialog.getSaveFileName(self, 'save file', exit_file_name, "*."+file_type)
        if to_file_path:
            ResourcePath = gol.get_value("ResourcePath")
            exit_file_path = os.path.join(ResourcePath, "file","dia",exit_file_name)
            t = CopyFileThread(exit_file_path,to_file_path)  # 目标函数
            t.start()  # 启动线程


    def save_result(self):
        '''
        设置保存结果位置
        '''
        directory = QFileDialog.getExistingDirectory(self, "file Path", "")
        if directory is not None and directory != "":
            gol.set_value("dia_result_path", directory)
            self.resultEdit.append(str(self.step)+".结果路径："+ directory)
            self.step += 1

    def rbclicked(self):
        if self.bg1.checkedId() == 11:
            self.simpleNameBtn.setDisabled(True)
        else:
            self.simpleNameBtn.setDisabled(False)

    def expression_data_import(self):
        '''
        导入DIA-NN结果文件文件
        '''
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                                   "(*.txt *.csv *.xlsx *.xls *.tsv)")
        if fileName is not None and fileName!="":
            self.resultEdit.append(str(self.step)+".DIANN的结果数据："+fileName)
            self.step += 1
            gol.set_value("diann_expression_data_path", fileName)

    def simple_name_import(self):
        '''
        导入File.Name对应的样本名称文件
        '''
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                                   "(*.txt *.csv *.xlsx *.xls *.tsv)")
        if fileName is not None and fileName!="":
            self.resultEdit.append(str(self.step)+".File.Name对应的样本名称文件："+fileName)
            self.step += 1
            gol.set_value("diann_simple_name_path", fileName)

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

    def certain(self):
        if gol.get_value("diann_expression_data_path") and gol.get_value("dia_result_path"):
            protein_group_header = self.proteinColname.currentText()
            gol.set_value("dia_protein_group_header", protein_group_header)
            self.step += 1
            self.resultEdit.append(str(self.step) + ".数据分析中...")
            self.main_thread = DIAQThread()
            self.main_thread.error_trigger.connect(self.error_display)
            self.main_thread.info_trigger.connect(self.info_display)
            self.main_thread.start()
        else:
            QMessageBox.warning(self, "提示", "请先导入DIANN结果数据和设置结果路径！")