# from screenshots generate training data (600*600 roiimg)

from process_img import getroi

import os
import cv2


frompath = 'E:\\My_temp\\Jump\\jump_capture03\\'
fromidx = 0
aimpath = 'E:\\Projects\\Coding\\wechat-jump\\v2.0_python\\__data\\02\\'
aimidx = 25
aimsize = 100

global rdat
if aimidx > 0:
    with open(aimpath + 'lbl.dat', 'rb') as rd:
        rdat = rd.read(aimidx * 16)

with open(aimpath + 'lbl.dat', 'wb') as wtlbl:
    if aimidx > 0:
        wtlbl.write(rdat)
    dirs = os.listdir(frompath)
    while fromidx < 200:
        if (str(fromidx) + '.png') in dirs:
            srcimg = cv2.imread(frompath + str(fromidx) + '.png')
            bx, by = getroi(srcimg)
            roiimg = srcimg[by:(by + 600), bx:(bx + 600)].copy()
            cv2.imwrite(aimpath + str(aimidx).zfill(3) + '.png', roiimg)
            rd = open(frompath + str(fromidx) + '.dat', 'rb')
            data = rd.read(16)
            wtlbl.write(data)
            aimidx += 1
        fromidx += 1
        if aimidx == aimsize:
            break
print(fromidx)
print(aimidx)
