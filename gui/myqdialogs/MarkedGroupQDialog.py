from PyQt5.QtWidgets import QDialog,QVBoxLayout, QLabel,QPushButton, QComboBox, QHBoxLayout, QTextEdit,QDesktopWidget,QMessageBox
from PyQt5.QtCore import Qt
import util.Global as gol
from util.Util import get_group_list


class MarkedGroupQDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def initUI(self,resultEdit,label,groups_num):
        '''
        resultEdit:打印分析流程中进展
        label：标记一下是那种情况下的分析，如无标记定量蛋白质组学分析，对应的label为label_free_pro
        groups_num：无标记对应的是2，有标记对应3：阴性与阳性与内参组
        '''
        self.label = label
        self.setWindowTitle('设置分组')

        """
        调整窗口大小为屏幕的宽高的0.35倍
        """
        screen = QDesktopWidget().screenGeometry()
        window_width = int(screen.width()*0.35)
        window_height = int(screen.height()*0.35)
        self.setMinimumWidth(window_width)
        self.setMinimumHeight(window_height)

        # self.setWindowFlags(Qt.WindowMinMaxButtonsHint)

        ### 设置对话框类型
        self.setWindowFlags(Qt.Tool)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        ## 查看分的group
        groupEdit = QTextEdit(self)
        groupEdit.setReadOnly(True)
        groupEdit.append("数据分组情况:")
        groups = get_group_list(f"{label}_information_path")
        groupEdit.append(str(groups))
        layout.addWidget(groupEdit)

        hLayout1 = QHBoxLayout()
        hLayout1.setSpacing(10)
        label2 = QLabel("阴性: ", self)
        self.cb1 = QComboBox()
        self.cb1.addItems(groups)
        self.cb1.setCurrentIndex(0)
        label3 = QLabel("阳性: ", self)
        self.cb2 = QComboBox()
        self.cb2.addItems(groups)
        self.cb2.setCurrentIndex(0)
        label4 = QLabel("质控组: ", self)
        self.cb3 = QComboBox()
        self.cb3.addItems(groups)
        self.cb3.setCurrentIndex(0)
        hLayout1.addWidget(label2)
        hLayout1.addWidget(self.cb1)
        hLayout1.addStretch(1)
        hLayout1.addWidget(label3)
        hLayout1.addWidget(self.cb2)
        hLayout1.addStretch(1)
        hLayout1.addWidget(label4)
        hLayout1.addWidget(self.cb3)
        layout.addLayout(hLayout1)

        hLayout2 = QHBoxLayout()
        hLayout2.addStretch(1)
        certainBtn = QPushButton('确定', self, objectName='ClickBtn')
        certainBtn.setStyleSheet("background: #83c5be")
        certainBtn.clicked.connect(lambda:self.certain(resultEdit))
        hLayout2.addWidget(certainBtn)
        layout.addLayout(hLayout2)

        if groups_num != len(groups):
            groupEdit.append(f"分组数量发生错误，应该有{groups_num}组，实际有{len(groups)}组")
            self.cb1.setDisabled(True)
            self.cb2.setDisabled(True)
            self.cb3.setDisabled(True)
            certainBtn.setDisabled(True)

    def certain(self,resultEdit):
        negativeGroup = self.cb1.currentText()
        positiveGroup = self.cb2.currentText()
        QCGroup = self.cb3.currentText()
        if negativeGroup==positiveGroup or negativeGroup==QCGroup or QCGroup==positiveGroup:
            QMessageBox.warning(self, "提示", "阴性、阳性、质控组都应该不同,请重新选择！")
        else:
            resultEdit.append("阴性组："+negativeGroup+" 阳性组为:"+positiveGroup+"质控组为："+QCGroup)
            gol.set_value(self.label+"_ngroup",negativeGroup)
            gol.set_value(self.label+"_pgroup",positiveGroup)
            gol.set_value(self.label+"_qcgroup",QCGroup)
            self.close()




