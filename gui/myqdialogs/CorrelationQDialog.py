from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QTextEdit, \
    QDesktopWidget, QMessageBox, QScrollArea, QWidget
from PyQt5.QtCore import Qt
import util.Global as gol


class CorrelationQDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.correlation_dict = {}
        self.total_samples = 0

    def initUI(self,resultEdit,label,ngroup_samples, pgroup_samples):
        '''
        resultEdit:打印分析流程中进展
        label：标记一下是那种情况下的分析，如无标记定量蛋白质组学分析，对应的label为label_free_pro
        '''
        self.label = label
        self.setWindowTitle('设置配对样本关系')

        self.total_samples = len(ngroup_samples)*2

        """
        调整窗口大小为屏幕的宽高的0.35倍
        """
        screen = QDesktopWidget().screenGeometry()
        window_width = int(screen.width()*0.4)
        window_height = int(screen.height()*0.4)
        self.setMinimumWidth(window_width)
        self.setMinimumHeight(window_height)

        # self.setWindowFlags(Qt.WindowMinMaxButtonsHint)

        ### 设置对话框类型
        self.setWindowFlags(Qt.Tool)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        vlayout1 = QVBoxLayout()
        vlayout1.setSpacing(10)

        for i in range(len(ngroup_samples)):
            # logger.info(f"第{i}组")
            self.correlation_dict[i]={"ngroup":ngroup_samples[i],"pgroup":pgroup_samples[i]}
            hLayout1 = QHBoxLayout()
            hLayout1.setSpacing(10)
            label1 = QLabel("第"+str(i+1)+"组：",self)
            label2 = QLabel("阴性: ", self)
            cb1 = QComboBox()
            cb1.addItems(ngroup_samples)
            cb1.setCurrentIndex(i)
            cb1.currentIndexChanged.connect(
                                    lambda: self.ngroup_select_change(cb1.currentText(),i))
            label3 = QLabel("阳性: ", self)
            cb2 = QComboBox()
            cb2.addItems(pgroup_samples)
            cb2.setCurrentIndex(i)
            cb2.currentIndexChanged.connect(
                lambda: self.pgroup_select_change(cb2.currentText(), i))
            hLayout1.addWidget(label1)
            hLayout1.addWidget(label2)
            hLayout1.addWidget(cb1)
            hLayout1.addStretch(1)
            hLayout1.addWidget(label3)
            hLayout1.addWidget(cb2)
            hLayout1.addStretch(1)
            vlayout1.addLayout(hLayout1)

        hLayout2 = QHBoxLayout()
        hLayout2.addStretch(1)
        certainBtn = QPushButton('确定', self, objectName='ClickBtn')
        certainBtn.setStyleSheet("background: #83c5be")
        certainBtn.clicked.connect(lambda:self.certain(resultEdit))
        hLayout2.addWidget(certainBtn)

        self.scrollAreaWidgetContents.setLayout(vlayout1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        layout.addWidget(self.scrollArea)
        layout.addLayout(hLayout2)

    def ngroup_select_change(self,ngroup,i):
        if self.correlation_dict[i]["ngroup"]!=ngroup:
            self.correlation_dict[i]["ngroup"] = ngroup

    def pgroup_select_change(self,pgroup,i):
        if self.correlation_dict[i]["pgroup"]!=pgroup:
            self.correlation_dict[i]["pgroup"] = pgroup

    def certain(self,resultEdit):
        # 先判断下
        total_list = []
        for value in self.correlation_dict.values():
            total_list.append(value["ngroup"])
            total_list.append(value["pgroup"])
        if self.total_samples == len(set(total_list)):
            resultEdit.append("您选择的配对样本信息为："+str(self.correlation_dict))
            gol.set_value(self.label + "_correlation_dict", self.correlation_dict)
            self.close()
        else:
            QMessageBox.warning(self, "提示", "配对样本中有样本选择多次，请重新选择！")




