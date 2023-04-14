from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsPixmapItem, QGraphicsScene, \
    QGraphicsView
import os
import util.Global as gol


class FunctionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.step = 1

    def scale_image(self, pil_image):  # 参数是：要适应的窗口宽、高、Image.open后的图片
        w_box = gol.get_value("window_width")*0.7
        h_box = gol.get_value("window_height")*0.7
        w, h = pil_image.width(), pil_image.height() # 获取图像的原始大小
        f1 = 1.0*w_box/w
        f2 = 1.0 * h_box / h
        factor = min([f1, f2])
        width = int(w * factor)
        height = int(h * factor)
        return pil_image.scaled(width, height)

    def initUI(self):
        layout = QVBoxLayout(self)
        # 加载首页图片
        ResourcePath = gol.get_value("ResourcePath")
        indexPath = os.path.join(ResourcePath, "img","function","function_analysis.png")
        pil_image = QImage(indexPath)
        scale_image = self.scale_image(pil_image)
        pix = QPixmap.fromImage(scale_image)
        self.item = QGraphicsPixmapItem(pix)  # 创建像素图元
        self.scene = QGraphicsScene()  # 创建场景
        self.scene.addItem(self.item)
        self.picshow = QGraphicsView()
        self.picshow.setScene(self.scene)  # 将场景添加至视图
        layout.addWidget(self.picshow)