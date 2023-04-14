from PyQt5.QtWidgets import QDialog,QVBoxLayout,QPushButton, QHBoxLayout, QTextEdit,QDesktopWidget
from PyQt5.QtCore import Qt


class HintQDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def initUI(self,title,text):
        self.setWindowTitle(title)

        """
        调整窗口大小为屏幕的宽高的0.35倍
        """
        screen = QDesktopWidget().screenGeometry()
        window_width = int(screen.width()*0.35)
        window_height = int(screen.height()*0.35)
        self.setMinimumWidth(window_width)
        self.setMinimumHeight(window_height)

        ### 设置对话框类型
        self.setWindowFlags(Qt.Tool)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        ## 查看分的group
        groupEdit = QTextEdit(self)
        groupEdit.setReadOnly(True)
        groupEdit.append(text)
        layout.addWidget(groupEdit)


        hLayout2 = QHBoxLayout()
        hLayout2.addStretch(1)
        certainBtn = QPushButton('close', self, objectName='ClickBtn')
        certainBtn.setStyleSheet("background: #83c5be")
        certainBtn.clicked.connect(self.certain)
        hLayout2.addWidget(certainBtn)
        layout.addLayout(hLayout2)

    def certain(self):
        self.close()