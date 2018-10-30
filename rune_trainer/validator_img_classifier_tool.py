# -*- coding:utf-8 -*-
import cv2, os, glob



w,h = 60,60


os.chdir("validation_data")
images = glob.glob("*.png")
for _img in images:

    if "-" in _img:
        continue
    print(_img)
    cropped = cv2.imread(_img)
    cv2.imshow("", cropped)
    dt = cv2.waitKeyEx(0)
    if dt == 2490368:
        os.rename(_img, _img.split(".")[0]+"-up"+".png")
        img_path = "up"
    elif dt == 2621440:
        os.rename(_img, _img.split(".")[0] + "-down" + ".png")
        img_path = "down"
    elif dt == 2424832:
        os.rename(_img, _img.split(".")[0] + "-left" + ".png")
        img_path = "left"
    elif dt == 2555904:
        os.rename(_img, _img.split(".")[0] + "-right" + ".png")
        img_path = "right"
    else:
        pass
