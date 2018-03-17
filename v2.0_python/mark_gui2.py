from process_img import getroi, getlines

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QFont

import numpy as np

import cv2
import sys
import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

path = r'E:\My_temp\Jump\data1\0.png'

red = QtGui.QColor(255, 0, 0)


class MyImgLabel(QtWidgets.QLabel):
	mouse_move_signal = QtCore.pyqtSignal()
	mouse_press_signal = QtCore.pyqtSignal()
	mouse_release_signal = QtCore.pyqtSignal()

	def __init__(self, mainwindow):
		super().__init__(mainwindow)
		self.mw = mainwindow
		self.setMouseTracking(True)

	def mousePressEvent(self, e: QtGui.QMouseEvent):
		self.mw.mousex = e.x() + self.geometry().x()
		self.mw.mousey = e.y() + self.geometry().y()
		self.mouse_press_signal.emit()

	def mouseReleaseEvent(self, e: QtGui.QMouseEvent):
		self.mw.mousex = e.x() + self.geometry().x()
		self.mw.mousey = e.y() + self.geometry().y()
		self.mouse_release_signal.emit()

	def mouseMoveEvent(self, e: QtGui.QMouseEvent):
		self.mw.mousex = e.x() + self.geometry().x()
		self.mw.mousey = e.y() + self.geometry().y()
		self.mouse_move_signal.emit()


class MainWindow(QtWidgets.QMainWindow):

	def __init__(self):
		super().__init__()

		self.setGeometry(200, 100, 900, 800)
		self.setWindowTitle('Labeling jump img_data')
		self.setWindowIcon(QtGui.QIcon('format.ico'))
		self.statusBar().showMessage('StandBy...')
		self.setMouseTracking(True)

		# 相关变量初始化
		self.mousex = 0
		self.mousey = 0
		self.roiimg = np.zeros((600, 600), dtype=int)
		self.boundingbox_visible = False
		self.img_info = {'x': 0, 'y': 0, 'ratio': 1}
		self.vtc_slc = False
		self.hrz_slc = False

		self.imglabel = MyImgLabel(self)
		self.imglabel.mouse_move_signal.connect(self.testfunc)
		self.imglabel.setGeometry(100, 100, 600, 600)
		self.imglabel.setPixmap(QtGui.QPixmap.fromImage(
			QtGui.QImage(self.roiimg.data, self.roiimg.shape[1], self.roiimg.shape[0],
						 QtGui.QImage.Format_RGB888)))

	# self.imglabel 鼠标移动信号触发槽
	def testfunc(self):
		pass

	def mousePressEvent(self, e: QtGui.QMouseEvent):
		pass

	def mouseMoveEvent(self, e: QtGui.QMouseEvent):
		self.mousex = e.x()
		self.mousey = e.y()
		self.statusBar().showMessage(
			'moving: ' + str(self.mousex) + ' , ' + str(self.mousey))

	def wheelEvent(self, event: QtGui.QWheelEvent):
		imgrect = self.imglabel.geometry()
		ratio = self.img_info['ratio']
		delta = event.angleDelta().y()
		# x,y 为映射不变点坐标
		if event.x() > imgrect.x() and event.x() < (imgrect.x() + imgrect.width()) and \
				event.y() > imgrect.y() and event.y() < (imgrect.y() + imgrect.height()):
			x = int(event.x() - imgrect.x())
			y = int(event.y() - imgrect.y())
		else:
			x = imgrect.width() // 2
			y = imgrect.height() // 2
		# 根据 delta 来判断滚轮方向
		if delta > 0:
			self.resizeImg(x, y, ratio + 0.5, x, y)
		if delta < 0:
			if ratio > 1:
				self.resizeImg(x, y, ratio - 0.5, x, y)

	# 图像映射：ratio0 → ratio1，(x0,y0) → (x1,y1)
	def resizeImg(self, x0, y0, ratio1, x1, y1):
		if ratio1 == 1:
			self.img_info['x'] = 0
			self.img_info['y'] = 0
			self.img_info['ratio'] = 1
			self.imglabel.setPixmap(QtGui.QPixmap.fromImage(
				QtGui.QImage(self.roiimg.data, self.roiimg.shape[1],
							 self.roiimg.shape[0], QtGui.QImage.Format_RGB888)))
			return
		imgrect = self.imglabel.geometry()
		anchor_x = self.img_info['x']
		anchor_y = self.img_info['y']
		ratio0 = self.img_info['ratio']
		# p 为 (x0,y0) 对应 ratio=1 时的坐标
		px = int((x0 - anchor_x) / ratio0)
		py = int((y0 - anchor_y) / ratio0)
		anchor_x = int(x1 - px * ratio1)
		anchor_y = int(y1 - py * ratio1)
		# (imgx,imgy) 为要显示图像起点坐标
		imgx = -anchor_x
		imgy = -anchor_y
		# 处理边界情况
		if imgx < 0:
			imgx = 0
		if imgx + imgrect.width() > int(imgrect.width() * ratio1):
			imgx = int(imgrect.width() * ratio1) - imgrect.width()
		if imgy < 0:
			imgy = 0
		if imgy + imgrect.height() > int(imgrect.height() * ratio1):
			imgy = int(imgrect.height() * ratio1) - imgrect.height()
		rszroi = self.roiimg[int(imgy / ratio1):int((imgy + imgrect.height()) / ratio1),
				 int(imgx / ratio1):int((imgx + imgrect.width()) / ratio1)].copy()
		curimg = cv2.resize(rszroi, (imgrect.height(), imgrect.width()),
							cv2.INTER_NEAREST)
		# 显示图像
		self.imglabel.setPixmap(QtGui.QPixmap.fromImage(
			QtGui.QImage(curimg.data, curimg.shape[1], curimg.shape[0],
						 QtGui.QImage.Format_RGB888)))
		# 更新信息
		self.img_info['x'] = anchor_x
		self.img_info['y'] = anchor_y
		self.img_info['ratio'] = ratio1

	# 移动图像：(x0,y0) → (x1,y1)
	def moveimg(self, x0, y0, x1, y1):
		imgrect = self.imglabel.geometry()
		anchor_x = self.img_info['x']
		anchor_y = self.img_info['y']
		ratio1 = self.img_info['ratio']
		imgx = -anchor_x + (x1 - x0)
		imgy = -anchor_y + (y1 - y0)
		if imgx < 0:
			imgx = 0
		if imgx + imgrect.width() > int(imgrect.width() * ratio1):
			imgx = int(imgrect.width() * ratio1) - imgrect.width()
		if imgy < 0:
			imgy = 0
		if imgy + imgrect.height() > int(imgrect.height() * ratio1):
			imgy = int(imgrect.height() * ratio1) - imgrect.height()
		rszroi = self.roiimg[int(imgy / ratio1):int((imgy + imgrect.height()) / ratio1),
				 int(imgx / ratio1):int((imgx + imgrect.width()) / ratio1)].copy()
		curimg = cv2.resize(rszroi, (imgrect.height(), imgrect.width()),
							cv2.INTER_NEAREST)
		self.imglabel.setPixmap(QtGui.QPixmap.fromImage(
			QtGui.QImage(curimg.data, curimg.shape[1], curimg.shape[0],
						 QtGui.QImage.Format_RGB888)))
		self.img_info['x'] = -imgx
		self.img_info['y'] = -imgy

	def keyPressEvent(self, event: QtGui.QKeyEvent):
		if event.key() == QtCore.Qt.Key_F1:
			srcimg = cv2.imread(path)
			bx, by = getroi(srcimg)
			self.roiimg = srcimg[by:(by + 600), bx:(bx + 600)].copy()
			self.roiimg = cv2.cvtColor(self.roiimg, cv2.COLOR_BGR2RGB)
			self.imglabel.setPixmap(QtGui.QPixmap.fromImage(
				QtGui.QImage(self.roiimg.data, self.roiimg.shape[1], self.roiimg.shape[0],
							 QtGui.QImage.Format_RGB888)))

		if event.key() == QtCore.Qt.Key_1:
			if self.hrz_slc:
				self.hrz_slc = False
				self.statusBar().showMessage('Standby...')
			else:
				self.hrz_slc = True
				self.vtc_slc = False
				self.statusBar().showMessage('choose horizontal line')

		if event.key() == QtCore.Qt.Key_2:
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
