# from screenshots generate training data (600*600 roiimg)

from process_img import getroi, augdata, delta_hsv

import os
import cv2
import random
import struct

idx_table = [0, 85, 140, 105, 98, 69, 71, 76, 214, 257, 236]
part = 2
bsize = 675
batch = 1024

if part == 1:
    datapath = 'E:\\My_temp\\Jump\\jump_capture'
    for i in range(1024):
        savepath = 'E:\\Projects\\Coding\\wechat-jump\\v2.0_python\\__data\\origin\\' + \
                   str(i // batch).zfill(2) + '\\' + str(i % batch).zfill(4)
        idx = random.randint(0, 640)

        p1 = 0
        p2 = idx
        while (p2 >= idx_table[p1]):
            p2 = p2 - idx_table[p1]
            p1 += 1
        roiimg, data = augdata(datapath + str(p1).zfill(2) + '\\' + str(p2), dpos=0)

        cv2.imwrite(savepath + '.png', roiimg)
        wt = open(savepath + '.dat', 'wb')
        wt.write(struct.pack('4i', data[0], data[1], data[2], data[3]))
        wt.close()






elif part == 2:
    datapath = 'E:\\My_temp\\Jump\\jump_capture'
    zeropath = 'E:\\My_temp\\Jump\\zero_label\\'
    for i in range(45000):
        savepath = 'E:\\Projects\\Coding\\wechat-jump\\v2.0_python\\__data\\augment\\' + \
                   str(i // batch).zfill(2) + '\\' + str(i % batch).zfill(4)
        prob = random.random()
        print(str(i).zfill(5) + ': ' + str(prob)[0:5],end='   __  ')
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
