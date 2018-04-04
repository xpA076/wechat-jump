# verify data_augmentation's correctness
# similar with verify_label.py (a little, little adjustment from that file)
# data_augmentation 没问题，但显示图片时有个玄学问题没法解决，每次程序都崩溃，晕

from process_img import augdata

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QFont

import cv2
import ctypes
import sys


ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
mainpath = 'E:\\My_temp\\Jump\\jump_capture'


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(200, 100, 1000, 900)
        self.setWindowTitle('label verification')
        self.setWindowIcon(QtGui.QIcon('format.ico'))
        self.statusBar().showMessage('Standby...')

        self.imglabel = QtWidgets.QLabel(self)
        self.imglabel.setGeometry(50, 50, 675, 675)

        self.label1 = QtWidgets.QLabel('data batch:', self)
        self.label1.setGeometry(770, 120, 180, 50)
        self.label1.setFont(QFont('Roman times', 20, QFont.Bold))

        self.label1 = QtWidgets.QLabel('data index:', self)
        self.label1.setGeometry(770, 270, 180, 50)
        self.label1.setFont(QFont('Roman times', 20, QFont.Bold))

        self.text1 = QtWidgets.QLineEdit('1', self)
        self.text1.setGeometry(850, 180, 50, 30)
        self.text1.setAlignment(QtCore.Qt.AlignRight)
        self.text1.setFont(QFont('楷体', 15, QFont.Bold))

        self.text2 = QtWidgets.QLineEdit('0', self)
        self.text2.setGeometry(850, 330, 50, 30)
        self.text2.setAlignment(QtCore.Qt.AlignRight)
        self.text2.setFont(QFont('楷体', 15, QFont.Bold))


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
            roiimg, data = augdata(
                mainpath + self.text1.text().zfill(2) + '\\' + self.text2.text())
            if (roiimg is None) or (data is None):
                raise FileNotFoundError
        except FileNotFoundError:
            msg = 'cannot open file:   \'' + mainpath + self.text1.text().zfill(2) + \
                  '\\' + self.text2.text() + '  may not exist'
            self.statusBar().showMessage(msg)
            return

        cv2.line(roiimg, (0, data[0]), (675, data[0]), (255, 0, 0), 1)
        cv2.line(roiimg, (0, data[1]), (675, data[1]), (255, 0, 0), 1)
        cv2.line(roiimg, (data[2], 0), (data[2], 675), (255, 0, 0), 1)
        cv2.line(roiimg, (data[3], 0), (data[3], 675), (255, 0, 0), 1)
        roiimg = cv2.cvtColor(roiimg, cv2.COLOR_BGR2RGB)
        # show image
        cv2.imwrite('test.png', roiimg)
        tstimg = QtGui.QImage(roiimg.data, 675, 675, QtGui.QImage.Format_RGB888)
        self.imglabel.setPixmap(QtGui.QPixmap.fromImage(tstimg))
        self.statusBar().showMessage('Standby...')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    wind = MainWindow()
    wind.show()
    sys.exit(app.exec_())
