from process_img import getroi, getlines

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QFont

import cv2
import sys
import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

path = r'E:\My_temp\Jump\data1\0.png'

srcimg = cv2.imread(path)
bx, by = getroi(srcimg)

roiimg = srcimg[by:(by + 600), bx:(bx + 600)].copy()


# cv2.imshow('a', roiimg)

# cv2.waitKey(0)

class MyImgLabel(QtWidgets.QLabel):
	mouse_move_signal = QtCore.pyqtSignal()

	def __init__(self, mainwindow):
		super().__init__(mainwindow)
		self.mw = mainwindow
		self.setMouseTracking(True)

	def mouseMoveEvent(self, e: QtGui.QMouseEvent):
		self.mw.mousex = e.x() + 100
		self.mw.mousey = e.y() + 100
		self.mouse_move_signal.emit()


# self.update()


"""
	def paintEvent(self, a0: QtGui.QPaintEvent):
		paint=QtGui.QPainter()
		paint.begin(self)
		pen=QtGui.QPen(QtCore.Qt.black,1,QtCore.Qt.SolidLine)
		paint.drawLine(20,20,self.mousex,self.mousey)
		paint.end()
"""


class MainWindow(QtWidgets.QMainWindow):
	red = QtGui.QColor(255, 0, 0)
	mousex = 0
	mousey = 0
	lines = []
	boundingbox_visible = False

	def __init__(self):
		super().__init__()

		self.setGeometry(200, 100, 900, 800)
		self.setWindowTitle('Labeling jump img_data')
		self.setWindowIcon(QtGui.QIcon('format.ico'))
		self.statusBar().showMessage('StandBy...')

		self.setMouseTracking(True)

		self.imglabel = MyImgLabel(self)
		self.imglabel.mouse_move_signal.connect(self.testfunc)
		self.imglabel.setGeometry(100, 100, 600, 600)

		bx, by = getroi(srcimg)
		self.roiimg = srcimg[by:(by + 600), bx:(bx + 600)].copy()
		self.imglabel.setPixmap(QtGui.QPixmap.fromImage(
			QtGui.QImage(self.roiimg, self.roiimg.shape[1], self.roiimg.shape[0],
						 QtGui.QImage.Format_RGB888)))

		self.lineu = QtWidgets.QWidget(self)
		self.lines.append(self.lineu)
		self.lined = QtWidgets.QWidget(self)
		self.lines.append(self.lined)
		self.linel = QtWidgets.QWidget(self)
		self.lines.append(self.linel)
		self.liner = QtWidgets.QWidget(self)
		self.lines.append(self.liner)
		for line in self.lines:
			line.setStyleSheet('QWidget{background-color:%s}' % self.red.name())
			line.setVisible(self.boundingbox_visible)

	def testfunc(self):
		self.update_boundingbox('vis', self.mousex - 100, self.mousex + 100,
								self.mousey - 50, self.mousey + 50)

	def update_boundingbox(self, cmd, x1=0, x2=0, y1=0, y2=0):
		if cmd == 'clr':
			if not self.boundingbox_visible:
				return
			self.boundingbox_visible = False
			for line in self.lines:
				line.setVisible(self.boundingbox_visible)
			return
		if not self.boundingbox_visible:
			self.boundingbox_visible = True
			for line in self.lines:
				line.setVisible(self.boundingbox_visible)
		self.lineu.setGeometry(x1, y1, x2 - x1, 1)
		self.lined.setGeometry(x1, y2, x2 - x1, 1)
		self.linel.setGeometry(x1, y1, 1, y2 - y1)
		self.liner.setGeometry(x2, y1, 1, y2 - y1)

	def mousePressEvent(self, e: QtGui.QMouseEvent):
		pass

	def mouseMoveEvent(self, e: QtGui.QMouseEvent):
		self.mousex = e.x()
		self.mousey = e.y()
		self.statusBar().showMessage(
			'moving: ' + str(e.x()) + ' , ' + str(e.y()))
		self.update_boundingbox('clr')


"""
	def paintEvent(self, a0: QtGui.QPaintEvent):
		paint = QtGui.QPainter()
		paint.begin(self)
		pen = QtGui.QPen(QtCore.Qt.red,1)
		paint.drawLine(20, 20, self.lbl.mousex, self.lbl.mousey)
		self.lbl.setPixmap(QtGui.QPixmap.fromImage(
			QtGui.QImage(roiimg, roiimg.shape[1], roiimg.shape[0],
						 QtGui.QImage.Format_RGB888)))
		paint.end()
		"""

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	wind = MainWindow()
	wind.show()
	sys.exit(app.exec_())
