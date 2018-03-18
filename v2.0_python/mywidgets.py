from PyQt5 import QtWidgets, QtGui, QtCore

import numpy as np
import cv2

red = QtGui.QColor(255, 0, 0)


class MyImgLabel(QtWidgets.QLabel):
	mouse_move_signal = QtCore.pyqtSignal()
	mouse_press_signal = QtCore.pyqtSignal()
	mouse_release_signal = QtCore.pyqtSignal()

	def __init__(self, mainwindow, roiimg=None):
		super().__init__(mainwindow)
		self.mw = mainwindow
		self.setMouseTracking(True)
		self.ismld = False  # isMouseLeftKeyDown (bool)
		self.img_info = {'x': 0, 'y': 0, 'ratio': 1}
		if roiimg is not None:
			self.roiimg = roiimg
			self.setImage(roiimg)
		self.lines = []
		self.lines.append(QtWidgets.QWidget(self))
		self.lines.append(QtWidgets.QWidget(self))
		self.lines.append(QtWidgets.QWidget(self))
		self.lines.append(QtWidgets.QWidget(self))
		for line in self.lines:
			line.setVisible(False)
			line.setStyleSheet('QWidget{background-color:%s}' % red.name())
		# TODO data同步
		self.data=[0,0,0,0]

	def setImage(self, roiimg):
		self.roiimg = roiimg
		self.setPixmap(QtGui.QPixmap.fromImage(
			QtGui.QImage(roiimg.data, self.geometry().width(), self.geometry().height(),
						 QtGui.QImage.Format_RGB888)))

	# 鼠标事件对应两部分功能：选择line / 移动img
	def mousePressEvent(self, e: QtGui.QMouseEvent):
		self.ismld = True
		if (self.mw.hrz_slc or self.mw.vtc_slc):
			# TODO 未计算比例
			if self.mw.hrz_slc:
				self.addLine(y=e.y())
			if self.mw.vtc_slc:
				self.addLine(x=e.x())
		else:
			self.mousex = e.x()
			self.mousey = e.y()

	def mouseMoveEvent(self, e: QtGui.QMouseEvent):
		if not self.ismld:
			return
		if (self.mw.hrz_slc or self.mw.vtc_slc):
			pass  # TODO
		else:
			self.moveimg(self.mousex, self.mousey, e.x(), e.y())
			self.mousex = e.x()
			self.mousey = e.y()

	def mouseReleaseEvent(self, e: QtGui.QMouseEvent):
		self.ismld = False

	# 图像映射：ratio0 →(d_ratio)→ ratio1，(x0,y0) → (x1,y1)
	def resizeImg(self, x0, y0, d_ratio, x1, y1):
		ratio1 = self.img_info['ratio'] + d_ratio
		if ratio1 < 1.1:
			self.img_info['x'] = 0
			self.img_info['y'] = 0
			self.img_info['ratio'] = 1
			self.setPixmap(QtGui.QPixmap.fromImage(
				QtGui.QImage(self.roiimg.data, self.roiimg.shape[1],
							 self.roiimg.shape[0], QtGui.QImage.Format_RGB888)))
			return
		imgrect = self.geometry()
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
		self.setPixmap(QtGui.QPixmap.fromImage(
			QtGui.QImage(curimg.data, curimg.shape[1], curimg.shape[0],
						 QtGui.QImage.Format_RGB888)))
		# 更新信息
		self.img_info['x'] = anchor_x
		self.img_info['y'] = anchor_y
		self.img_info['ratio'] = ratio1

	# 移动图像：(x0,y0) → (x1,y1)
	def moveimg(self, x0, y0, x1, y1):
		if self.img_info['ratio'] == 1:
			return
		imgrect = self.geometry()
		anchor_x = self.img_info['x']
		anchor_y = self.img_info['y']
		ratio1 = self.img_info['ratio']
		imgx = -anchor_x - (x1 - x0)
		imgy = -anchor_y - (y1 - y0)
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
		self.setPixmap(QtGui.QPixmap.fromImage(
			QtGui.QImage(curimg.data, curimg.shape[1], curimg.shape[0],
						 QtGui.QImage.Format_RGB888)))
		self.img_info['x'] = -imgx
		self.img_info['y'] = -imgy

	# 对 bounding box 边线的操作
	def addLine(self, x=-1, y=-1):
		if x >= 0:
			if not self.lines[0].isVisible():
				self.curline = self.lines[0]
			elif not self.lines[1].isVisible():
				self.curline = self.lines[1]
				if self.lines[0].geometry().x() > x:
					self.lines[1].setGeometry(self.lines[0].geometry().x(), 0,
											  1, self.geometry().height())
					self.curline = self.lines[0]
			else:
				self.mw.statusBar().showMessage('cannot add vertical line')
				return
			self.curline.setGeometry(x, 0, 1, self.geometry().height())
			self.curline.setVisible(True)
		elif y >= 0:
			if not self.lines[2].isVisible():
				self.curline = self.lines[2]
			elif not self.lines[3].isVisible():
				self.curline = self.lines[3]
				if self.lines[2].geometry().y() > y:
					self.lines[3].setGeometry(0, self.lines[2].geometry().y(),
											  self.geometry().width(), 1)
					self.curline = self.lines[2]
			else:
				self.mw.statusBar().showMessage('cannot add horizontal line')
				return
			self.curline.setGeometry(0, y, self.geometry().width(), 1)
			self.curline.setVisible(True)

	def moveLine(self,idx=-1,x=-1,y=-1):
		if idx==-1:
			if x>=0:
				self.curline.setGeometry(x, 0, 1, self.geometry().height())
			elif y>=0:
				self.curline.setGeometry(0, y, self.geometry().width(), 1)
		else:
			# TODO 对应idx图像移动
			pass

	def deleteLine(self,idx=-1):
		if idx==-1:
			self.curline.setVisible(False)
		else:
			self.lines[idx].setVisible(False)
