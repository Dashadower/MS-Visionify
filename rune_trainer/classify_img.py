# -*- coding:utf-8 -*-
import cv2, os, glob
import numpy as np
print(os.getcwd())
os.chdir("images/cropped")
last_img_name = None
img_path = None
for _img in glob.glob("*.png"):

    img = cv2.imread(_img)
    if img_path is not None:
        os.rename(last_img_name, "traindata/"+img_path+"/"+last_img_name)
    cv2.imshow("",img)
    dt = cv2.waitKeyEx(0)
    print(dt)
    if dt == 2490368:
        last_img_name = _img
        img_path = "up"
    elif dt == 2621440:
        last_img_name = _img
        img_path = "down"
    elif dt == 2424832:
        last_img_name = _img
        img_path = "left"
    elif dt == 2555904:
        last_img_name = _img
        img_path = "right"
    else:
        last_img_name = _img
        img_path = None