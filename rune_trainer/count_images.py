# -*- coding:utf-8 -*-
# -*- coding:utf-8 -*-
"""
Merge two directories of up,down,left,right images
"""
import os, cv2, glob

categories = ["up", "down", "left", "right"]
dir = "traindata"

os.chdir("images/cropped")

for cat in categories:
    files = glob.glob("%s/%s/*.png"%(dir, cat))
    print(cat, len(files))


