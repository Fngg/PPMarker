from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal


class MyLabel2(QLabel):
    mylabelSig = pyqtSignal(str)
    mylabelDoubleClickSig = pyqtSignal(str)

    def __int__(self):
        super(MyLabel2, self).__init__()

    def mouseDoubleClickEvent(self, e):  # 双击
        sigContent = self.objectName()
        self.mylabelDoubleClickSig.emit(sigContent)

    def mousePressEvent(self, e):  # 单击
        sigContent = self.objectName()
        self.mylabelSig.emit(sigContent)

    # def leaveEvent(self, e):  # 鼠标离开label
    #     print("leaveEvent")
    #
    # def enterEvent(self, e):  # 鼠标移入label
    #     print("enterEvent")


class MyQLabel(QLabel):
    # 自定义信号, 注意信号必须为类属性
    button_clicked_signal = pyqtSignal()

    def mouseReleaseEvent(self, QMouseEvent):
        self.button_clicked_signal.emit()

    # 可在外部与槽函数连接
    def connect_customized_slot(self, func):
        self.button_clicked_signal.connect(func)
