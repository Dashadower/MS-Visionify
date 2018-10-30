# -*- coding:utf-8 -*-
import sys
sys.path.append("../src")
from screen_processor import MapleScreenCapturer

import cv2, os, time, glob, imutils
import numpy as np



cap = MapleScreenCapturer()

img_to_work_on = None
x, y, w, h = 450, 180, 500, 130
clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(8,8))

min_dist = 30
min_r = 15
max_r = 27
hough_ksize = 2.0
img_arr = None

while True:
    img = cap.capture(set_focus=False)
    img_arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    final_img = imutils.resize(img_arr, width = 500)
    cv2.imshow("q to save image", final_img)
    inp = cv2.waitKey(1)
    if inp == ord("q"):
        cv2.destroyAllWindows()
        img_to_work_on = img_arr[y:y + h, x:x + w]
        img_arr = img_arr[y:y + h, x:x + w]
        break


hsv_img = cv2.cvtColor(img_arr, cv2.COLOR_BGR2HSV)
# Maximize saturation
hsv_img[:,:,1] = 255
hsv_img[:,:,2] = 255
hsv_img_rgb = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
hsv_gray = cv2.cvtColor(hsv_img_rgb, cv2.COLOR_BGR2GRAY)
lab = cv2.cvtColor(img_to_work_on, cv2.COLOR_BGR2LAB)
l, a, b = cv2.split(lab)
l2 = clahe.apply(l)
lab = cv2.merge((l2, a, b))
img_to_work_on = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
img_to_work_on = cv2.cvtColor(img_to_work_on, cv2.COLOR_BGR2GRAY)
#img_to_work_on = cv2.equalizeHist(img_to_work_on)
eqed = cv2.equalizeHist(img_to_work_on)
circles = cv2.HoughCircles(img_to_work_on, cv2.HOUGH_GRADIENT, hough_ksize, min_dist, minRadius=min_r, maxRadius=max_r)
circle_roi = []

img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2GRAY)
#img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
cv2.imshow("histogram", np.vstack([img_arr, img_to_work_on, eqed, hsv_gray]))
cv2.waitKey(0)
if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    for (_x, _y, _r) in circles:
        cropped = img_arr[max(0, int(_y - 60 / 2)):int(_y + 60 / 2), max(0, int(_x - 60 / 2)):int(_x + 60 / 2)]
        #circle_roi.append([np.reshape(cropped, [1,60,60,3]), (_x,_y), cropped])


circle_roi = sorted(circle_roi, key=lambda x: x[1][0])
