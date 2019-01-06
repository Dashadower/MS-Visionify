"""
RGB to Grayscale batch converter.
"""
import os, cv2, glob

categories = ["up", "down", "left", "right"]
subdirs = ["external_images"]

os.chdir("images/cropped")

for fdir in subdirs:
    for cat in categories:
        files = glob.glob("%s/%s/*.png"%(fdir, cat))
        for file in files:
            img = cv2.imread(file)
            ds = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            # Maximize saturation
            ds[:, :, 1] = 255
            ds[:, :, 2] = 255
            ds = cv2.cvtColor(ds, cv2.COLOR_HSV2BGR)
            ds = cv2.cvtColor(ds, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(file, ds)
            print(file, "done")
