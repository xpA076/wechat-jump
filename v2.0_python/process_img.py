import cv2
import numpy as np
import struct
import os
import random


# get coordinate of starting point
def __get_pawnpos(srcimg):
    grayimg = cv2.cvtColor(srcimg, cv2.COLOR_BGR2GRAY)
    unit = cv2.imread('unit.jpg', 0)
    minval, maxval, minpt, maxpt = cv2.minMaxLoc(
        cv2.matchTemplate(grayimg, unit, cv2.TM_SQDIFF_NORMED))
    start_pos = [minpt[0] + 38, minpt[1] + 190]
    return start_pos


# get roi bounding_box
def getroi(srcimg, bw=600, bh=600):
    start_pos = __get_pawnpos(srcimg)
    # if not at boundary: ↓
    # point:(bx + 300, by + 300) is centrosymmetric with start_pos (pawn_position)
    # but roi_bounding_box's height / width may not be 600 (defined by parameters: bw, bh)
    bx = (srcimg.shape[1] - start_pos[0] - 300)
    by = (srcimg.shape[0] - start_pos[1] - 300)
    if bx < 0:
        bx = 0
    elif (bx + bw) >= srcimg.shape[1]:
        bx = srcimg.shape[1] - bw
    if by < 0:
        by = 0
    elif (by + bh) >= srcimg.shape[0]:
        by = srcimg.shape[0] - bh
    return int(bx), int(by)


def getlines(roiimg):
    x_list = []
    canny = cv2.Canny(roiimg, 15, 30)
    lines = cv2.HoughLines(canny, 1, np.pi / 180, 80)
    for line in lines:
        rho = line[0][0]
        theta = line[0][1]
        if abs(theta) < 0.1:
            x_list.append(rho)
    return x_list


def augdata(path, bw=675, bh=675, dpos=True, dh=True, ds=True, dv=True):
    try:
        srcimg = cv2.imread(path + '.png')
        # width and height in absolute coordination
        absw = srcimg.shape[1]
        absh = srcimg.shape[0]
        if srcimg is None:
            raise FileNotFoundError
        rd = open(path + '.dat', 'rb')
    except FileNotFoundError:
        print('cannot open path:  ' + path)
        raise FileNotFoundError

    # delta position (calculate in absolute coordination)
    bx0, by0 = getroi(srcimg)
    lbl_relative = struct.unpack('4i', rd.read(16))
    lbl_abs = [0] * 4
    lbl_abs[0] = lbl_relative[0] + by0
    lbl_abs[1] = lbl_relative[1] + by0
    lbl_abs[2] = lbl_relative[2] + bx0
    lbl_abs[3] = lbl_relative[3] + bx0
    bx1, by1 = getroi(srcimg, bw=bw, bh=bh)  # if not dpos, upleft_pos: (bx1, by1)
    if dpos:
        prob = random.random()
        limit = [(lbl_abs[0] * 5 + lbl_abs[1]) // 6, (lbl_abs[0] + lbl_abs[1] * 5) // 6,
                 (lbl_abs[2] * 5 + lbl_abs[3]) // 6, (lbl_abs[2] + lbl_abs[3] * 5) // 6]
        # there is 0.7 probablity that label has a chance to be outside of bounding_box
        if prob < 0.7:
            t = limit
        else:
            t = lbl_abs
        # 下面这段仔细算一下就明白为什么了。绝对坐标系下 bx1, by1 各有若干限制
        bx1 = random.randint(max(0, t[3] - bw), min(absw - bw, t[2]))
        by1 = random.randint(max(400, t[1] - bh), min(absh - bh, t[0]))
    data = [0] * 4
    data[0] = lbl_abs[0] - by1
    data[1] = lbl_abs[1] - by1
    data[2] = lbl_abs[2] - bx1
    data[3] = lbl_abs[3] - bx1

    roiimg = srcimg[by1:(by1 + bh), bx1:(bx1 + bw)].copy()

    roiimg = delta_hsv(roiimg, dh, ds, dv)

    # check for error(debuging)
    if roiimg.shape[0] != 675 or roiimg.shape[1] != 675:
        raise AssertionError
    outsidex = max(0 - data[2], data[3] - bw)
    outsidey = max(0 - data[0], data[1] - bh)
    if outsidey * 5 > data[1] - data[0] or outsidex * 5 > data[3] - data[2]:
        raise AssertionError
    # return
    return roiimg, data


def delta_hsv(roiimg, dh=True, ds=True, dv=True):
    hsvroi = cv2.cvtColor(roiimg, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsvroi)
    # delta hue
    if dh:
        dHue = random.randint(0, 179)
        h = (h + dHue) % 180
        print('dHue: ' + str(dHue), end=' ;')
    # delta saturation
    if ds:
        s = s.astype(np.float)
        max_ = np.max(s)
        dSature = random.randint(0, 255)
        print('Sature: d=' + str(dSature) + '; max: ' + str(max_),end=' ;')
        s = (s * dSature / max(max_, 10))
        s = s.astype(np.uint8)
    # delta value
    if dv:
        dratio = random.random() * 0.2 - 0.1
        print('dRatio: ' + str(dratio))
        if dratio < 0:
            v = (1 + dratio) * v
        else:
            v = 255 * dratio + (1 - dratio) * v
        v = v.astype(np.uint8)
    hsvroi = cv2.merge([h, s, v])
    rtnimg = cv2.cvtColor(hsvroi, cv2.COLOR_HSV2BGR)
    return rtnimg
