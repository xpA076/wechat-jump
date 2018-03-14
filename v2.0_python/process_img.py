import cv2

def getroi(srcimg):
	unit=cv2.imread('unit.jpg',0)
	img_g=cv2.cvtColor(srcimg,cv2.COLOR_BGR2GRAY)
	minval,maxval,minpt,maxpt=cv2.minMaxLoc(cv2.matchTemplate(img_g,unit,cv2.TM_SQDIFF_NORMED))
	begin_pos=[minpt[0]+19,minpt[1]+95]