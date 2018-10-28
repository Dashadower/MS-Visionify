# -*- coding:utf-8 -*-
import cv2, os, glob
import numpy as np



min_dist = 30
min_r = 15
max_r = 27
hough_ksize = 2.0

w,h = 60,60


#traindata_path = os.path.join(os.getcwd(), "images\\cropped\\testdata")
traindata_path = os.path.join(os.getcwd(), "images\\cropped\\traindata")
os.chdir("images/screenshots")
images = glob.glob("*.png")
numberofphotos = int((open("../cropped/labeldata.txt", "r").read()))
print(numberofphotos)
clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(8,8))
total = 0
last_img_name = None
img_path = None
for _img in images:
    print(_img)
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
            cropped = color[max(0,int(y-h/2)):int(y+h/2), max(0,int(x-w/2)):int(x+w/2)]
            cv2.imshow("", cropped)
            dt = cv2.waitKeyEx(0)
            if dt == 2490368:

                cv2.imwrite(os.path.join(traindata_path, "up", "%d.png"%(numberofphotos+total+1)), cropped)
                print(os.path.join(traindata_path, "up", "%d.png"%(numberofphotos+total+1)))
                total += 1
                img_path = "up"
            elif dt == 2621440:
                cv2.imwrite(os.path.join(traindata_path, "down", "%d.png" % (numberofphotos + total + 1)), cropped)
                print(os.path.join(traindata_path, "down", "%d.png"%(numberofphotos+total+1)))
                total += 1
                img_path = "down"
            elif dt == 2424832:
                cv2.imwrite(os.path.join(traindata_path, "left", "%d.png" % (numberofphotos + total + 1)), cropped)
                print(os.path.join(traindata_path, "left", "%d.png"%(numberofphotos+total+1)))
                total += 1
                img_path = "left"
            elif dt == 2555904:
                cv2.imwrite(os.path.join(traindata_path, "right", "%d.png" % (numberofphotos + total + 1)), cropped)
                print(os.path.join(traindata_path, "right", "%d.png"%(numberofphotos+total+1)))
                total += 1
                img_path = "right"
            else:
                pass
with open("../cropped/labeldata.txt", "w") as b:
    b.write(str(numberofphotos+total))
print("added %d new images"%(total))