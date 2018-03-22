from PyQt5 import QtWidgets, QtGui

import cv2

color1 = QtGui.QColor(255, 0, 0)  # 已固定line颜色
color2 = QtGui.QColor(0, 0, 255)  # 当前选择line颜色


class MyImgLabel(QtWidgets.QLabel):

    # 其实加一个 refresh() 方法逻辑会清晰许多

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
        self.curline = None
        for line in self.lines:
            line.setVisible(False)
            line.setStyleSheet('QWidget{background-color:%s}' % color1.name())
        self.data = [-1, -1, -1, -1]  # index--{↑:0, ↓:1, ←:2, →:3}
        self.curidx = -1  # current selection of line's index
        self.mousex = 0
        self.mousey = 0
        self.msg = None


    def setImage(self, roiimg):
        self.roiimg = roiimg
        self.setPixmap(QtGui.QPixmap.fromImage(
            QtGui.QImage(roiimg.data, self.geometry().width(), self.geometry().height(),
                QtGui.QImage.Format_RGB888)))
        self.data = [-1, -1, -1, -1]
        self.curidx = -1
        self.updateLines()


    # 鼠标事件对应两部分功能：选择line / 移动img
    def mousePressEvent(self, e: QtGui.QMouseEvent):
        self.ismld = True
        if self.mw.hrz_slc or self.mw.vtc_slc:
            if self.mw.hrz_slc:
                self.addLine(y=self.pos2data(y=e.y()))
            if self.mw.vtc_slc:
                self.addLine(x=self.pos2data(x=e.x()))
        else:
            self.mousex = e.x()
            self.mousey = e.y()


    def mouseMoveEvent(self, e: QtGui.QMouseEvent):
        if not self.ismld:
            return
        if self.mw.hrz_slc or self.mw.vtc_slc:
            dst = 0  # useless line
            if self.mw.hrz_slc:
                if e.y() < 0:
                    dst = self.pos2data(y=0)
                elif e.y() > self.geometry().height() - 1:
                    dst = self.pos2data(y=self.geometry().height() - 1)
                else:
                    dst = self.pos2data(y=e.y())
            if self.mw.vtc_slc:
                if e.x() < 0:
                    dst = self.pos2data(x=0)
                elif e.x() > self.geometry().width() - 1:
                    dst = self.pos2data(x=self.geometry().width() - 1)
                else:
                    dst = self.pos2data(x=e.x())
            self.moveLine(self.curidx, dst)
        else:
            self.moveimg(self.mousex, self.mousey, e.x(), e.y())
            self.mousex = e.x()
            self.mousey = e.y()


    def mouseReleaseEvent(self, e: QtGui.QMouseEvent):
        self.ismld = False
        self.mw.clearfunc(self.msg)
        self.msg = None


    # 图像映射：ratio0 →(+ d_ratio)→ ratio1，(x0,y0) → (x1,y1)
    def resizeImg(self, x0, y0, d_ratio, x1, y1):
        ratio1 = self.img_info['ratio'] + d_ratio
        if ratio1 < 1.1:
            self.img_info['x'] = 0
            self.img_info['y'] = 0
            self.img_info['ratio'] = 1
            self.setPixmap(QtGui.QPixmap.fromImage(
                QtGui.QImage(self.roiimg.data, self.roiimg.shape[1],
                    self.roiimg.shape[0], QtGui.QImage.Format_RGB888)))
            self.updateLines()
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
        self.updateLines()


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
        self.updateLines()
        self.img_info['x'] = -imgx
        self.img_info['y'] = -imgy
        self.updateLines()


    # 对 bounding box 边线的操作（add/move/delete 所有关于坐标的参数均在 self.data 坐标系下表示）
    def addLine(self, x=-1, y=-1):
        if y >= 0:
            if self.data[0] == -1:
                self.data[0] = y
                self.curidx = 0
            elif self.data[1] >= 0:
                self.msg = 'cannot add more vertical line'
                self.curidx = -1
            elif self.data[0] == y:
                self.msg = 'current line is coincident with previous line'
                self.curidx = -1
            elif self.data[0] > y >= 0:
                self.data[1] = self.data[0]
                self.data[0] = y
                a = self.lines[0]
                self.lines[0] = self.lines[1]
                self.lines[1] = a
                self.curidx = 0
            else:
                self.data[1] = y
                self.curidx = 1
        if x >= 0:
            if self.data[2] == -1:
                self.data[2] = x
                self.curidx = 2
            elif self.data[3] >= 0:
                self.msg = 'cannot add more horizontal line'
                self.curidx = -1
            elif self.data[2] == x:
                self.msg = 'current line is coincident with previous line'
                self.curidx = -1
            elif self.data[2] > x >= 0:
                self.data[3] = self.data[2]
                self.data[2] = x
                a = self.lines[2]
                self.lines[2] = self.lines[3]
                self.lines[3] = a
                self.curidx = 2
            else:
                self.data[3] = x
                self.curidx = 3
        self.updateLines()


    def moveLine(self, idx, dst):  # dst: short of destination
        if idx >= 0 and self.lines[idx].isVisible():
            if dst < 0:
                self.data[idx] = 0
            elif 0 <= idx <= 1 and dst >= self.geometry().height():
                self.data[idx] = self.geometry().height() - 1
            elif 2 <= idx <= 3 and dst >= self.geometry().width():
                self.data[idx] = self.geometry().width() - 1
            else:
                self.data[idx] = dst
            self.updateLines()


    def deleteLine(self, idx=-1):
        if idx >= 0:
            if idx == 0 and self.data[1] >= 0:
                self.data[0] = self.data[1]
                self.data[1] = -1
            elif idx == 2 and self.data[3] >= 0:
                self.data[2] = self.data[3]
                self.data[3] = -1
            else:
                self.data[idx] = -1
            self.curidx = -1
            self.updateLines()


    # 用 self.data 的信息更新显示 lines（其实图像显示逻辑也可以放到这里面来）
    def updateLines(self):
        for i in range(4):
            if self.data[i] >= 0:
                self.lines[i].setVisible(True)
                if i <= 1:
                    self.lines[i].setGeometry(0, self.data2pos(y=self.data[i]),
                        self.geometry().width(), 1)
                else:
                    self.lines[i].setGeometry(self.data2pos(x=self.data[i]), 0,
                        1, self.geometry().height())
                if i == self.curidx:
                    self.lines[i].setStyleSheet(
                        'QWidget{background-color:%s}' % color2.name())
                else:
                    self.lines[i].setStyleSheet(
                        'QWidget{background-color:%s}' % color1.name())
            else:
                self.lines[i].setVisible(False)


    # 鼠标坐标系 与 self.data坐标系 的互相换算
    def pos2data(self, x=-1, y=-1):
        if x >= 0:
            return int(round((x - self.img_info['x']) / self.img_info['ratio']))
        if y >= 0:
            return int(round((y - self.img_info['y']) / self.img_info['ratio']))


    def data2pos(self, x=-1, y=-1):
        if x >= 0:
            return int(x * self.img_info['ratio'] + self.img_info['x'])
        if y >= 0:
            return int(y * self.img_info['ratio'] + self.img_info['y'])


    def setcuridx(self, idx):
        self.curidx = idx
        self.updateLines()
