# verify label's correctness

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QFont

import cv2
import ctypes
import sys
import struct


ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
mainpath = 'E:\\Projects\\Coding\\wechat-jump\\v2.0_python\\__data\\'


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(200, 100, 900, 750)
        self.setWindowTitle('label verification')
        self.setWindowIcon(QtGui.QIcon('format.ico'))
        self.statusBar().showMessage('Standby...')

        self.imglabel = QtWidgets.QLabel(self)
        self.imglabel.setGeometry(50, 50, 600, 600)

        self.label1 = QtWidgets.QLabel('data batch:', self)
        self.label1.setGeometry(670, 120, 180, 50)
        self.label1.setFont(QFont('Roman times', 20, QFont.Bold))

        self.label1 = QtWidgets.QLabel('data index:', self)
        self.label1.setGeometry(670, 270, 180, 50)
        self.label1.setFont(QFont('Roman times', 20, QFont.Bold))

        self.text1 = QtWidgets.QLineEdit('0', self)
        self.text1.setGeometry(750, 180, 50, 30)
        self.text1.setAlignment(QtCore.Qt.AlignRight)
        self.text1.setFont(QFont('楷体', 15, QFont.Bold))

        self.text2 = QtWidgets.QLineEdit('0', self)
        self.text2.setGeometry(750, 330, 50, 30)
        self.text2.setAlignment(QtCore.Qt.AlignRight)
        self.text2.setFont(QFont('楷体', 15, QFont.Bold))

        #self.btn=QtWidgets.QPushButton('',self)
        #self.btn.setGeometry(770,500,20,20)


    def keyPressEvent(self, e: QtGui.QKeyEvent):
        if e.key() == QtCore.Qt.Key_F1:
            self.updateimg()

        if e.key() == QtCore.Qt.Key_PageDown:
            idx = int(self.text1.text())
            self.text1.setText(str(idx + 1))
            self.updateimg()

        if e.key() == QtCore.Qt.Key_PageUp:
            idx = int(self.text1.text())
            if idx == 0:
                return
            self.text1.setText(str(idx - 1))
            self.updateimg()

        if e.key() == QtCore.Qt.Key_F11:
            idx = int(self.text2.text())
            self.text2.setText(str(idx - 1))
            if idx == 0:
                return
            self.updateimg()

        if e.key() == QtCore.Qt.Key_F12:
            idx = int(self.text2.text())
            self.text2.setText(str(idx + 1))
            self.updateimg()


    def updateimg(self):
        # get image data
        try:
            roiimg = cv2.imread(mainpath + self.text1.text().zfill(2) + '\\' +
                                self.text2.text().zfill(3) + '.png')
            if roiimg is None:
                raise FileNotFoundError
        except FileNotFoundError:
            msg = 'cannot open file:   \'' + mainpath + self.text1.text().zfill(2) + \
                  '\\' + self.text2.text().zfill(3) + '.png\'   may not exist'
            self.statusBar().showMessage(msg)
            return
        else:
            roiimg = cv2.cvtColor(roiimg, cv2.COLOR_BGR2RGB)
        # get label data
        try:
            rd = open(mainpath + self.text1.text().zfill(2) + '\\lbl.dat', 'rb')
            idx = int(self.text2.text())
            rd.seek(16 * idx, 0)
            data = struct.unpack('4i', rd.read(16))
            cv2.line(roiimg, (0, data[0]), (600, data[0]), (255, 0, 0), 1)
            cv2.line(roiimg, (0, data[1]), (600, data[1]), (255, 0, 0), 1)
            cv2.line(roiimg, (data[2], 0), (data[2], 600), (255, 0, 0), 1)
            cv2.line(roiimg, (data[3], 0), (data[3], 600), (255, 0, 0), 1)
        except FileNotFoundError:
            self.statusBar().showMessage('label data error')
            return
        # show image
        self.imglabel.setPixmap(QtGui.QPixmap.fromImage(
            QtGui.QImage(roiimg.data, 600, 600, QtGui.QImage.Format_RGB888)))
        self.statusBar().showMessage('Standby...')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    wind = MainWindow()
    wind.show()
    sys.exit(app.exec_())
