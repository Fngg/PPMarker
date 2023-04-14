'''
富集分析：GO和KEGG
'''

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
    QTextEdit, QLabel, QPushButton, QComboBox, QMessageBox, QFileDialog, QDialog
from PyQt5.QtCore import Qt
import os
import util.Global as gol
from gui.myqdialogs.ChoiceQDialog import ChoiceQDialog
from gui.mywidgets.MyQLable import MyQLabel
from gui.workQThead.UtilThread import CopyFileThread
from gui.workQThead.function_analysis.KmSurvivalQThead import KmSurvivalQThread
from util.Logger import logger


class SurvivalWidget(QWidget):
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
        self.resultEdit.append('''介绍：KM方法即Kaplan-Meier survival estimate是一种无参数方法来从观察的生存时间来估计生存概率和绘制生存曲线的方法。KM生存分析模型，描述了单个变量和生存之间的关系而忽略其他变量的影响。同时，Kaplan-Meier方法只能针对分类变量（如治疗A vs 治疗B，男 vs 女），对于连续变量如某基因的表达值可根据表达值的中位数将基因分为高低表达组，再来探究该基因高低表达对生存的影响。\n生存数据：要求导入的数据，行为样本，列包含生存时间、生存状态、感兴趣的基因或者其他临床特征。对于临床特征的值要求是二分类的值。\n结果解读：\n1. P值是log-rank test的p值，是衡量某个变量的二分类组对生存率的影响有没有显著差别，p<0.05表示为有显著差别，反之则无显著差别。\n2. Kaplan-Meier曲线（生存曲线）以生存时间为横轴,生存率S (tk)为纵轴，绘制而成的连续型的阶梯形曲线，用以说明生存时间与生存率之间的关系。生存曲线一般是平滑而水平延伸的，当某个时间点一旦有患者发生终点事件(如死亡)，曲线就会垂直下降,下降幅度是该时间点上患者发生终点事件例数和上一个时间节点后随访的患者样本量的比。\n\n''')


        vLayout1.addWidget(label2)
        vLayout1.addWidget(self.resultEdit)

        vLayout2 = QVBoxLayout()
        vLayout2.setSpacing(10)
        vLayout2.setAlignment(Qt.AlignTop)
        label3 =  QLabel("生存数据导入", self)
        label3.setStyleSheet("font-weight:bold")

        hLayout1 = QHBoxLayout()
        hLayout1.setSpacing(20)
        dataInputBtn = QPushButton(
            '生存数据', self, objectName='ClickBtn')
        dataInputBtn.clicked.connect(self.survival_data_import)
        dataInputBtn.setStyleSheet("background: #83c5be")
        label4 = MyQLabel("下载生存数据",self)
        label4.setStyleSheet("color:red;text-decoration:underline;")
        label4.connect_customized_slot(lambda: self.saveFile("unicox_example_data.xlsx"))
        hLayout1.addWidget(dataInputBtn)
        hLayout1.addWidget(label4)
        hLayout1.addStretch(1)

        label61 =  QLabel("设置对应的列", self)
        label61.setStyleSheet("font-weight:bold")

        hLayout71 = QHBoxLayout()
        hLayout71.setSpacing(10)
        label71 = QLabel("生存时间：",self)
        survivalTimeBtn = QPushButton(
            '生存时间', self, objectName='ClickBtn')
        survivalTimeBtn.setStyleSheet("background: #83c5be")
        survivalTimeBtn.clicked.connect(self.choice_survival_time)
        hLayout71.addWidget(label71)
        hLayout71.addWidget(survivalTimeBtn)
        hLayout71.addStretch(1)

        hLayout711 = QHBoxLayout()
        hLayout711.setSpacing(10)
        label711 = QLabel("时间单位：",self)
        self.survivalTimeType = QComboBox(self, minimumWidth=200)
        self.survivalTimeType.addItems(["天", "月", "年"])
        hLayout711.addWidget(label711)
        hLayout711.addWidget( self.survivalTimeType)
        hLayout711.addStretch(1)

        hLayout72 = QHBoxLayout()
        hLayout72.setSpacing(10)
        label72 = QLabel("生存状态：",self)
        survivalStatusBtn = QPushButton(
            '生存状态', self, objectName='ClickBtn')
        survivalStatusBtn.clicked.connect(self.choice_survival_status)
        survivalStatusBtn.setStyleSheet("background: #83c5be")
        hLayout72.addWidget(label72)
        hLayout72.addWidget(survivalStatusBtn)
        hLayout72.addStretch(1)

        label721 = QLabel("注：生存状态的值仅为0与1，1代表目标事件发生，0代表目标事件未发生或失访",self)


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
        vLayout2.addWidget(label61)
        vLayout2.addLayout(hLayout71)
        vLayout2.addLayout(hLayout711)
        vLayout2.addLayout(hLayout72)
        vLayout2.addWidget(label721)
        vLayout2.addWidget(label11)
        vLayout2.addLayout(hLayout7)
        vLayout2.addWidget(certainBtn)

        layout.addLayout(vLayout1,stretch=6)
        layout.addLayout(vLayout2,stretch=4)

    def choice_survival_status(self):
        '''
        设置生存状态
        '''
        km_survival_data_path = gol.get_value("km_survival_data_path")
        if km_survival_data_path:
            try:
                choiceQDialog = ChoiceQDialog()
                choiceQDialog.initUI(self.resultEdit, "km_survival_survival_status", "生存状态", km_survival_data_path)
                if choiceQDialog.exec_() == QDialog.Accepted:
                    pass
            except Exception as e:
                logger.error(e)
                logger.error(f"参数km_survival_data_path：{km_survival_data_path}")

    def choice_survival_time(self):
        '''
        设置分组信息
        '''
        km_survival_data_path = gol.get_value("km_survival_data_path")
        if km_survival_data_path:
            try:
                choiceQDialog = ChoiceQDialog()
                choiceQDialog.initUI(self.resultEdit, "km_survival_survival_time", "生存时间", km_survival_data_path)
                if choiceQDialog.exec_() == QDialog.Accepted:
                    pass
            except Exception as e:
                logger.error(e)
                logger.error(f"参数km_survival_data_path：{km_survival_data_path}")

    def saveFile(self, exit_file_name):
        file_type = exit_file_name.split(".")[-1]
        to_file_path, ftype = QFileDialog.getSaveFileName(self, 'save file', "km_survival_example_data", "*." + file_type)
        if to_file_path:
            ResourcePath = gol.get_value("ResourcePath")
            exit_file_path = os.path.join(ResourcePath, "file", "function_analysis", exit_file_name)
            t = CopyFileThread(exit_file_path, to_file_path)  # 目标函数
            t.start()  # 启动线程

    def survival_data_import(self):
        '''导入生存数据文件进行单因素cox'''
        fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                         "(*.txt *.csv *.xlsx *.xls *.tsv)")
        if fileName is not None and fileName != "":
            self.resultEdit.append(str(self.step) + ".导入的生存数据文件：" + fileName)
            self.step += 1
            gol.set_value("km_survival_data_path", fileName)

    def save_result(self):
        '''
        设置保存结果位置
        '''
        directory = QFileDialog.getExistingDirectory(self, "file Path", "")
        if directory is not None and directory != "":
            gol.set_value("km_survival_result_path", directory)
            self.resultEdit.append(str(self.step) + ".结果路径：" + directory)
            self.step += 1

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
        if gol.get_value("km_survival_result_path") and gol.get_value("km_survival_data_path") and gol.get_value(
                "km_survival_survival_time") and gol.get_value("km_survival_survival_status"):
            survivalTimeType_index = self.survivalTimeType.currentIndex()
            if survivalTimeType_index == 0:
                gol.set_value("km_survival_survival_time_type", "day")
            elif survivalTimeType_index == 1:
                gol.set_value("km_survival_survival_time_type", "month")
            elif survivalTimeType_index == 2:
                gol.set_value("km_survival_survival_time_type", "year")
            self.resultEdit.append(str(self.step) + ".数据分析中...")
            self.main_thread = KmSurvivalQThread()
            self.main_thread.error_trigger.connect(self.error_display)
            self.main_thread.info_trigger.connect(self.info_display)
            self.main_thread.start()
        else:
            QMessageBox.warning(self, "提示", "请先导入数据和设置参数！")
