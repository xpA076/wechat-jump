"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
用于标记样本的GUI：
页面主体imglabel对象实现：
    首张图片加载取决于全局变量 mainpath, startidx
	鼠标滚轮对应鼠标所在区域缩放
		鼠标滚轮对应已选中线条移动
	鼠标拖动对应图像移动（放大比率 ratio > 1 情况下）
		鼠标拖动对应已选中线条移动
	键盘z/x分别对应标注水平/竖直边框线操作（再按取消标注功能，在状态栏有显示）
	键盘 ↑↓←→ / wasd 对应选中线条单像素移动
	选中指定线条 1234键 （选中线条显示为不同颜色）
	del / ` 删除当前线条
	按下 Enter/Tab 后会在图片路径下生成同名dat文件，以二进制形式存储4条边线int型坐标
	    同时刷新下一张图片
	
键盘、滚轮事件写在主窗体下；鼠标按键事件写在MyImgLabel中
GUI还有好多小问题，但是已经能当工具用了，先不完善了
2018.3.22 11:48
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
from process_img import getroi
from mywidgets import MyImgLabel

from PyQt5 import QtWidgets, QtGui, QtCore


import cv2
import sys
import ctypes
import struct

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

# for initializing
mainpath = 'E:\\My_temp\\Jump\\jump_capture07\\'
startidx = 21


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.setGeometry(200, 100, 900, 800)
        self.setWindowTitle('Labeling jump img_data')
        self.setWindowIcon(QtGui.QIcon('format.ico'))
        self.statusBar().showMessage('StandBy...')
        self.setMouseTracking(True)

        # 相关变量初始化
        # 下面这两个bool值可以放在主窗体下也可以放在imglabel类下，现与键盘事件一同放在主窗体下
        self.vtc_slc = False
        self.hrz_slc = False
        self.imglabel = MyImgLabel(self)
        self.imglabel.setGeometry(100, 100, 600, 600)

        self.pathidx = startidx

        # show 1st img
        try:
            srcimg = cv2.imread(mainpath + str(self.pathidx) + '.png')
            if srcimg is None:
                raise IOError
        except IOError:
            self.statusBar().showMessage('cannot open file:    \'' + mainpath +
                                         str(self.pathidx) + '.png\'   may not exist')
        else:
            bx, by = getroi(srcimg)
            roiimg = srcimg[by:(by + 600), bx:(bx + 600)].copy()
            roiimg = cv2.cvtColor(roiimg, cv2.COLOR_BGR2RGB)
            self.imglabel.setImage(roiimg)



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
            self.imglabel.resizeImg(x, y, 1, x, y)
        if delta < 0:
            self.imglabel.resizeImg(x, y, -1, x, y)


    def keyPressEvent(self, event: QtGui.QKeyEvent):

        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Tab:
            self.clearfunc()
            # write data (check validation)
            if 0 <= self.imglabel.data[0] < self.imglabel.data[1] < \
                    self.imglabel.geometry().height() and 0 <= self.imglabel.data[2] < \
                    self.imglabel.data[3] < self.imglabel.geometry().width():
                wt = open(mainpath + str(self.pathidx) + '.dat', 'wb')
                dat = struct.pack('4i', self.imglabel.data[0], self.imglabel.data[1],
                    self.imglabel.data[2], self.imglabel.data[3])
                wt.write(dat)
                wt.close()
            else:
                self.statusBar().showMessage('invalid data: cannot save data')
                return
            self.pathidx += 1
            # open new image
            try:
                srcimg = cv2.imread(mainpath + str(self.pathidx) + '.png')
                if srcimg is None:
                    raise IOError
            except IOError:
                self.statusBar().showMessage('cannot open file:    \'' + mainpath +
                                             str(self.pathidx) + '.png\'   may not exist')
            else:
                bx, by = getroi(srcimg)
                roiimg = srcimg[by:(by + self.imglabel.geometry().height()),
                         bx:(bx + self.imglabel.geometry().width())].copy()
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

        if event.key() == QtCore.Qt.Key_1:
            self.imglabel.setcuridx(0)

        if event.key() == QtCore.Qt.Key_2:
            self.imglabel.setcuridx(1)

        if event.key() == QtCore.Qt.Key_3:
            self.imglabel.setcuridx(2)

        if event.key() == QtCore.Qt.Key_4:
            self.imglabel.setcuridx(3)

        if event.key() == QtCore.Qt.Key_Delete or event.key() == 96:  # 96 means ~
            self.imglabel.deleteLine(self.imglabel.curidx)
            self.clearfunc()

        if event.key() == QtCore.Qt.Key_W or event.key() == QtCore.Qt.Key_Up:
            if 0 <= self.imglabel.curidx <= 1:
                self.imglabel.moveLine(self.imglabel.curidx,
                    self.imglabel.data[self.imglabel.curidx] - 1)

        if event.key() == QtCore.Qt.Key_S or event.key() == QtCore.Qt.Key_Down:
            if 0 <= self.imglabel.curidx <= 1:
                self.imglabel.moveLine(self.imglabel.curidx,
                    self.imglabel.data[self.imglabel.curidx] + 1)

        if event.key() == QtCore.Qt.Key_A or event.key() == QtCore.Qt.Key_Left:
            if 2 <= self.imglabel.curidx <= 3:
                self.imglabel.moveLine(self.imglabel.curidx,
                    self.imglabel.data[self.imglabel.curidx] - 1)

        if event.key() == QtCore.Qt.Key_D or event.key() == QtCore.Qt.Key_Right:
            if 2 <= self.imglabel.curidx <= 3:
                self.imglabel.moveLine(self.imglabel.curidx,
                    self.imglabel.data[self.imglabel.curidx] + 1)

        if event.key() == QtCore.Qt.Key_Escape:
            self.clearfunc()


    def clearfunc(self, msg=None):
        self.vtc_slc = False
        self.hrz_slc = False
        if msg is None:
            self.statusBar().showMessage('Standby...')
        else:
            self.statusBar().showMessage(msg)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    wind = MainWindow()
    wind.show()
    sys.exit(app.exec_())
