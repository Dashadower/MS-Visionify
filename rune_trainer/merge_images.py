# -*- coding:utf-8 -*-
"""
Merge two directories of up,down,left,right images
"""
import os, cv2, glob

categories = ["up", "down", "left", "right"]
fromdir = "external_images"
todir = "traindata"
os.chdir("images/cropped")
numberofphotos = int(open("labeldata.txt", "r").read())
print(numberofphotos)


for cat in categories:
    files = glob.glob("%s/%s/*.png"%(fromdir, cat))
    for file in files:
        numberofphotos += 1
        os.rename(file, "%s/%s/%d.png"%(todir, cat, numberofphotos))
        #cv2.imwrite(file, ds)
        print(file, "done")

open("labeldata.txt", "w").write(str(numberofphotos))
