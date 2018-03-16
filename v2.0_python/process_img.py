import cv2
import numpy as np


# get coordinate of starting point
def __get_pawnpos(srcimg):
	grayimg=cv2.cvtColor(srcimg,cv2.COLOR_BGR2GRAY)
	unit = cv2.imread('unit.jpg', 0)
	minval, maxval, minpt, maxpt = cv2.minMaxLoc(
		cv2.matchTemplate(grayimg, unit, cv2.TM_SQDIFF_NORMED))
	start_pos = [minpt[0] + 38, minpt[1] + 190]
	return start_pos

# get roi bounding_box
def getroi(srcimg,bw=600,bh=600):
	start_pos=__get_pawnpos(srcimg)
	bx=(1080-start_pos[0]-bw/2)
	by=(1920-start_pos[1]-bh/2)
	if bx<0:
		bx=0
	elif (bx+bw)>=1080:
		bx=1080-bw
	return int(bx),int(by)


def getlines(roiimg):
	x_list=[]
	canny=cv2.Canny(roiimg,15,30)
	lines=cv2.HoughLines(canny,1,np.pi/180,80)
	for line in lines:
		rho=line[0][0]
		theta=line[0][1]
		if abs(theta)<0.1:
			x_list.append(rho)
	return x_list
