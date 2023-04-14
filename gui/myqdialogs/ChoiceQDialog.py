from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDesktopWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, \
    QMessageBox
import util.Global as gol
from util.Util import get_column_list
from util.Logger import logger


class ChoiceQDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def initUI(self,resultEdit,global_key,title,data_path):
        self.global_key = global_key
        self.title = title
        self.setWindowTitle(title)
        screen = QDesktopWidget().screenGeometry()
        window_width = int(screen.width()*0.2)
        window_height = int(screen.height()*0.2)
        self.setMinimumWidth(window_width)
        self.setMinimumHeight(window_height)

        self.setWindowFlags(Qt.Tool)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        columns = get_column_list(data_path)

        hLayout1 = QHBoxLayout()
        hLayout1.setSpacing(10)
        label2 = QLabel(title+": ", self)
        self.cb1 = QComboBox()
        self.cb1.addItems(columns)
        self.cb1.setCurrentIndex(0)
        hLayout1.addWidget(label2)
        hLayout1.addWidget(self.cb1)
        layout.addLayout(hLayout1)

        hLayout2 = QHBoxLayout()
        hLayout2.addStretch(1)
        certainBtn = QPushButton('确定', self, objectName='ClickBtn')
        certainBtn.setStyleSheet("background: #83c5be")
        certainBtn.clicked.connect(lambda: self.certain(resultEdit))
        hLayout2.addWidget(certainBtn)
        layout.addLayout(hLayout2)

    def certain(self,resultEdit):
        select_col = self.cb1.currentText()
        if select_col is not None and len(select_col)>=0:
            resultEdit.append(self.title + "列名：" + select_col)
            gol.set_value(self.global_key, select_col)
            self.close()
        else:
            QMessageBox.warning(self, "提示", "阴性类型应该与阳性类型不同,请重新选择！")

