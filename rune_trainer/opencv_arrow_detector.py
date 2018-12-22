# -*- coding:utf-8 -*-
import sys
sys.path.append("../src")
from screen_processor import MapleScreenCapturer
import cv2, time, imutils, math, glob, random
import numpy as np
cap = MapleScreenCapturer()
from win32gui import SetForegroundWindow



x, y, w, h = 450, 180, 500, 130
ds = None
while True:
    img = cap.capture(rect=[0,0,1600,900], set_focus=False)
    img_arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    final_img = imutils.resize(img_arr, width = 200)
    cv2.imshow("s to save image", final_img)
    inp = cv2.waitKey(1)



    if inp == ord("s"):
        SetForegroundWindow(cap.ms_get_screen_hwnd())
        time.sleep(0.3)
        ds = cap.capture(set_focus=False)
        ds = cv2.cvtColor(np.array(ds), cv2.COLOR_RGB2BGR)
        ds = ds[y:y + h, x:x + w]
        print("saved")

    elif inp == ord("q"):
        cv2.destroyAllWindows()
        break
    elif inp == ord("r"):
        imgpath = "C:\\Users\\tttll\\PycharmProjects\\MacroSTory\\rune_trainer\\images\\screenshots\\finished\\*.png"
        dt = random.choice(glob.glob(imgpath))

        ds = cv2.imread(dt)
        print("read data")

display = ds.copy()
gray = display.copy()
gray = cv2.cvtColor(gray, cv2.COLOR_BGR2HSV)
# Maximize saturation
gray[:, :, 1] = 255
gray[:, :, 2] = 255
gray = cv2.cvtColor(gray, cv2.COLOR_HSV2BGR)
gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
cv2.imwrite("validation_rgb.png", display)
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,1, gray.shape[0]/8 , param1=100, param2=30,minRadius=18, maxRadius=30)
circle_roi = []
if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    for (x, y, r) in circles:
        print(x, y, r)
        cropped_color = display[max(0, int(y - 60 / 2)):int(y + 60 / 2), max(0, int(x - 60 / 2)):int(x + 60 / 2)]
        cropped = gray[max(0,int(y-60/2)):int(y+60/2), max(0,int(x-60/2)):int(x+60/2)]
        cropped = cv2.erode(cropped, (3,3))
        cropped = cv2.dilate(cropped, (3,3))
        cropped = cv2.Canny(cropped, threshold1=120, threshold2=190)
        im2, contours, hierachy = cv2.findContours(cropped, cv2.RETR_TREE , cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(cropped_color,contours,-1,(167,143,255),1)
        temp = np.zeros([60,60], np.uint8)
        for y in range(0, 60):
            for x in range(0, 60):
                if (cropped_color[y,x].tolist() == [167,143,255]):
                    temp[y,x] = 255

        #cv2.circle(gray, (x, y), r, (0, 255, 0), 2)
        #cv2.circle(display, (x, y), r, (0, 255, 0), 2)
        circle_roi.append([temp, (x, y), cropped_color])

cv2.imshow("", display)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imshow("", gray)
cv2.waitKey(0)
cv2.destroyAllWindows()
circle_roi = sorted(circle_roi, key=lambda x: x[1][0])

circle_radius = 18

def distance(x1, y1, x2, y2):
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)


quadrants = [0,0,0,0]
for circ in circle_roi:
    circ_black = circ[0]
    circ_rgb = circ[2]
    center = circ[1]

    w = circ_black.shape[1]
    h = circ_black.shape[0]

    for y in range(0,h):
        for x in range(0,w):
            if distance(30,30, x, y) <= circle_radius:
                if circ_black[y,x] == 255:
                    fixed_x = x - 30
                    fixed_y = y - 30

                    if fixed_y > 0:
                        if fixed_x > 0:
                            quadrants[0] += 1
                        elif fixed_x < 0:
                            quadrants[1] += 1
                    elif fixed_y < 0:
                        if fixed_x > 0:
                            quadrants[3] += 1
                        elif fixed_x < 0:
                            quadrants[2] += 1

    print("top vs bottom", quadrants[0]+quadrants[1], quadrants[2]+quadrants[3])
    print("left vs right", quadrants[1]+quadrants[2], quadrants[0]+quadrants[3])
    cv2.circle(circ_rgb, (30, 30), circle_radius, (0, 255, 0), 2)
    cv2.imshow("", imutils.resize(circ_rgb, width=400))
    cv2.imshow("b",imutils.resize(circ_black, width=400))
    cv2.waitKeyEx(0)

