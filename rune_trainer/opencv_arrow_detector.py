# -*- coding:utf-8 -*-
import sys
sys.path.append("../src")
from screen_processor import MapleScreenCapturer
import cv2, time, imutils, math
import numpy as np
cap = MapleScreenCapturer()
from win32gui import SetForegroundWindow



x, y, w, h = 450, 180, 500, 130
ds = None
while True:
    img = cap.capture(set_focus=False)
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
        ds = cv2.imread("validation_rgb.png")
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
        cropped = gray[max(0,int(y-60/2)):int(y+60/2), max(0,int(x-60/2)):int(x+60/2)]
        cropped = cv2.Canny(cropped, threshold1=60, threshold2=180)
        cropped_color = display[max(0,int(y-60/2)):int(y+60/2), max(0,int(x-60/2)):int(x+60/2)]
        cv2.circle(gray, (x, y), r, (0, 255, 0), 2)
        #cv2.circle(display, (x, y), r, (0, 255, 0), 2)
        circle_roi.append([cropped, (x, y), cropped_color])

cv2.imshow("", display)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imshow("", gray)
cv2.waitKey(0)
cv2.destroyAllWindows()
circle_roi = sorted(circle_roi, key=lambda x: x[1][0])

for circ in circle_roi:
    circ_img = circ[0]
    _, contours, _ = cv2.findContours(circ_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    """for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
        if len(approx) >= 20:
            cv2.drawContours(circ[2],[cnt], -1,(0,255,0), 1)"""


    lines = cv2.HoughLinesP(circ[0],1,np.pi/180, 10,minLineLength=5)
    line_data = []
    for line in lines:
        x1, y1, x2, y2 = line[0].tolist()
        if x2 == x1 or y2 == y1:
            slope = 0
        else:
            slope = (y2-y1)/(x2-x1)
        line_data.append([x1,y1,x2,y2, slope])
        #cv2.line(circ[2], (x1, y1), (x2, y2), (0, 255, 0), 1)

    for line in line_data:
        for other_line in line_data:
            dist = []

            processed_slope = line[4] * other_line[4]
            if processed_slope <= 0:
                copied = circ[2].copy()
                cv2.line(copied, (line[0], line[1]),(line[2], line[3]), (0, 255, 0), 1)
                cv2.line(copied, (other_line[0], other_line[1]), (other_line[2], other_line[3]), (255, 0, 0), 1)
                #cv2.imshow(str(processed_slope), imutils.resize(copied, width=400))
                #cv2.waitKey(0)
                #cv2.destroyAllWindows()
    cv2.imshow("contours", imutils.resize(circ[2], width=400))
    cv2.imshow("canny",imutils.resize(circ[0], width=400))
    cv2.waitKey(0)
