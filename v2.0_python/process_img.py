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
        if srcimg is None:
            raise FileNotFoundError
        rd = open(path + '.dat', 'rb')
    except FileNotFoundError:
        print('cannot open path:  ' + path)
        print('return...')
        return None, None

    # delta position
    bx, by = getroi(srcimg)
    lbldata = struct.unpack('4i', rd.read(16))
    bx2, by2 = getroi(srcimg, bw=bw, bh=bh)
    ## recording delta x,y
    dx = bx2 - bx
    dy = by2 - by
    if dpos:
        t = [(lbldata[0] * 3 + lbldata[1]) // 4, (lbldata[0] + lbldata[1] * 3) // 4,
             (lbldata[2] * 3 + lbldata[3]) // 4, (lbldata[2] + lbldata[3] * 3) // 4]
        dx += random.randint(max(-bx, t[3] - bw), min(srcimg.shape[1] - bx, t[2]))
        dy += random.randint(max(-by, t[1] - bh), min(srcimg.shape[0] - by, t[0]))
    bx += dx
    by += dy
    data = [0] * 4
    data[0] = lbldata[0] - dy
    data[1] = lbldata[1] - dy
    data[2] = lbldata[2] - dx
    data[3] = lbldata[3] - dx
    roiimg = srcimg[by:(by + bh), bx:(bx + bw)].copy()

    hsvroi = cv2.cvtColor(roiimg, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsvroi)
    # delta hue
    if dh:
        h = (h + random.randint(0, 179)) % 180
    # delta saturation
    if ds:
        s = s.astype(np.float)
        s = (s * random.randint(0, 255) / np.max(s))
        s=s.astype(np.uint8)
    # delta value
    if dv:
        dratio = random.random() * 0.2 - 0.1
        if dratio < 0:
            v = (1 + dratio) * v
        else:
            v = 255 * dratio + (1 - dratio) * v
        v=v.astype(np.uint8)
    hsvroi = cv2.merge([h, s, v])
    roiimg = cv2.cvtColor(hsvroi, cv2.COLOR_HSV2BGR)

    # return
    return roiimg, data
