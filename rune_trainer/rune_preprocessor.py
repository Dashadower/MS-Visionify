# -*- coding:utf-8 -*-
import cv2, os, glob
import numpy as np
os.chdir("images/screenshots")
images = glob.glob("*.png")

min_dist = 30
min_r = 15
max_r = 27
hough_ksize = 2.0

w,h = 60,60
print(os.getcwd())

numberofphotos = int((open("../cropped/labeldata.txt", "r").read()))
print(numberofphotos)
clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(8,8))
total = 0
for _img in images:
    print(_img)
    os.chdir("../screenshots")
    img = cv2.imread(_img)
    color = img.copy()
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l2 = clahe.apply(l)
    lab = cv2.merge((l2, a, b))
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.equalizeHist(img)

    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, hough_ksize, min_dist, minRadius=min_r, maxRadius=max_r)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            print(x,y,r)
            print(int(y-h/2),int(y+h/2), int(x-w/2),int(x+w/2))
            cropped = color[max(0,int(y-h/2)):int(y+h/2), max(0,int(x-w/2)):int(x+w/2)]
            cv2.imshow("", cropped)
            dt = cv2.waitKey(0)
            if dt == ord("y"):
                total += 1
                os.chdir("../cropped")
                cv2.imwrite("%d.png"%(numberofphotos+total), cropped)

            else:
                pass
with open("../cropped/labeldata.txt", "w") as b:
    b.write(str(numberofphotos+total))
print("added %d new images"%(total))