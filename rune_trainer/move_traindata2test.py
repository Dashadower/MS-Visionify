# -*- coding:utf-8 -*-
import os, glob, random
os.chdir("images/cropped")

categories = ["up", "down", "left", "right"]

ops = int(input("Number of pictures from each category to move?"))

for cat in categories:
    opt = 0
    dirs = glob.glob("traindata\\%s\\*.png"%(cat))
    random.shuffle(dirs)
    for file in dirs:
        os.rename(file, "testdata\\%s\\%s"%(cat, file.split("\\")[-1]))
        print(file, "->", "testdata/%s/%s"%(cat, file.split("\\")[-1]))
        opt = opt + 1
        if opt >= ops:
            break
            #pass