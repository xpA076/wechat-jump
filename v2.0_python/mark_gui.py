"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
用于标记样本的GUI：
页面主体imglabel对象实现：
	F1 刷新显示图片 # TODO
	鼠标滚轮对应鼠标所在区域缩放
		鼠标滚轮对应已选中线条移动
	鼠标拖动对应图像移动（放大 ratio > 1 情况下）
		鼠标拖动对应已选中线条移动
	键盘z/x分别对应标注水平/竖直边框线（再按取消标注功能）
	鼠标单击/拖动对应选中边界线条显示/移动 （TODO 待绑定对应鼠标事件）	
	键盘 ↑↓←→ / wasd 对应选中线条单像素移动 TODO
	前一标过的线可按esc撤销 TODO
	
TODO: (undefined)
    选中指定线条 1234键
	删除指定线条 ~1234键
	图片导入逻辑
	生成 label_data 导出逻辑
	
键盘、滚轮事件写在主窗体下；鼠标按键事件写在MyImgLabel中
# TODO 信号槽事件功能待取消 
2018.3.19 23:27
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# TODO 边界线条相关功能尚未DeBug
from process_img import getroi, getlines
from mywidgets import MyImgLabel

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QFont

import numpy as np

import cv2
import sys
import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

path = r'E:\My_temp\Jump\data1\0.png'


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.setGeometry(200, 100, 900, 800)
        self.setWindowTitle('Labeling jump img_data')
        self.setWindowIcon(QtGui.QIcon('format.ico'))
        self.statusBar().showMessage('StandBy...')
        self.setMouseTracking(True)

        # 相关变量初始化
        # 这两个bool值可以放在主窗体下也可以放在imglabel类下，现与键盘事件一同放在主窗体下
        self.vtc_slc = False
        self.hrz_slc = False

        self.imglabel = MyImgLabel(self)
        self.imglabel.mouse_move_signal.connect(self.testfunc)
        self.imglabel.setGeometry(100, 100, 600, 600)


    # self.imglabel 鼠标移动信号触发槽
    def testfunc(self):
        pass


    def mousePressEvent(self, e: QtGui.QMouseEvent):
        pass


    def mouseMoveEvent(self, e: QtGui.QMouseEvent):
        pass


    def wheelEvent(self, event: QtGui.QWheelEvent):
        imgrect = self.imglabel.geometry()
        delta = event.angleDelta().y()
        # x,y 为映射不变点坐标
        if imgrect.x() < event.x() < (imgrect.x() + imgrect.width()) and \
                imgrect.y() < event.y() < (imgrect.y() + imgrect.height()):
            x = int(event.x() - imgrect.x())
            y = int(event.y() - imgrect.y())
        else:
            x = imgrect.width() // 2
            y = imgrect.height() // 2
        # 根据 delta 来判断滚轮方向
        if delta > 0:
            self.imglabel.resizeImg(x, y, 0.5, x, y)
        if delta < 0:
            self.imglabel.resizeImg(x, y, -0.5, x, y)


    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_F1:
            srcimg = cv2.imread(path)
            bx, by = getroi(srcimg)
            roiimg = srcimg[by:(by + 600), bx:(bx + 600)].copy()
            roiimg = cv2.cvtColor(roiimg, cv2.COLOR_BGR2RGB)
            self.imglabel.setImage(roiimg)

        if event.key() == QtCore.Qt.Key_Z:
            if self.hrz_slc:
                self.hrz_slc = False
                self.statusBar().showMessage('Standby...')
            else:
                self.hrz_slc = True
                self.vtc_slc = False
                self.statusBar().showMessage('choose horizontal line')

        if event.key() == QtCore.Qt.Key_X:
            if self.vtc_slc:
                self.vtc_slc = False
                self.statusBar().showMessage('Standby...')
            else:
                self.vtc_slc = True
                self.hrz_slc = False
                self.statusBar().showMessage('choose vertical line')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    wind = MainWindow()
    wind.show()
    sys.exit(app.exec_())
