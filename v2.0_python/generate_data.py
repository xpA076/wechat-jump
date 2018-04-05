# from screenshots generate training data (600*600 roiimg)

from process_img import getroi, augdata, delta_hsv

import os
import cv2
import random
import struct

"""
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
"""

idx_table = [0, 85, 140, 105, 98, 69, 71, 76, 214, 257, 236]

datapath = 'E:\\My_temp\\Jump\\jump_capture'
zeropath = 'E:\\My_temp\\Jump\\zero_label\\'
bsize = 675
batch = 1000
for i in range(45000):
    savepath = 'E:\\Projects\\Coding\\wechat-jump\\v2.0_python\\__data\\' + \
               str(i // batch).zfill(2) + '\\' + str(i % batch).zfill(4)
    prob = random.random()
    print(str(i) + ': ' + str(prob))
    # os.system('pause')
    if prob < 0.3:
        idx = random.randint(0, 43)
        srcimg = cv2.imread(zeropath + str(idx) + '.png')
        bx = random.randint(0, 1075 - bsize)
        by = random.randint(0, 1915 - bsize)
        roiimg = srcimg[by:(by + bsize), bx:(bx + bsize)].copy()
        roiimg = delta_hsv(roiimg)
        data = [0] * 4
    else:
        idx = random.randint(0, 640)
        p1 = 0
        p2 = idx
        while (p2 >= idx_table[p1]):
            p2 = p2 - idx_table[p1]
            p1 += 1
        roiimg, data = augdata(datapath + str(p1).zfill(2) + '\\' + str(p2))
    # save data and label
    cv2.imwrite(savepath + '.png', roiimg)
    wt = open(savepath + '.dat', 'wb')
    wt.write(struct.pack('4i', data[0], data[1], data[2], data[3]))
    wt.close()
