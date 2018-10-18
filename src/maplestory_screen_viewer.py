# -*- coding:utf-8 -*-
from screen_processor import MapleScreenCapturer
import cv2, imutils
import numpy as np
cap = MapleScreenCapturer()

while True:
    img = cap.capture(set_focus=False)
    img_arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    grayscale = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(grayscale, (7,7), 5)
    eroded = cv2.erode(blurred, (7,7))
    dilated = cv2.dilate(eroded, (7,7))
    #canny = cv2.Canny(eroded, threshold1=210, threshold2=255)
    #canny = imutils.resize(dilated, width = 500)
    final_img = img_arr

    cv2.imshow("", final_img)

    inp = cv2.waitKey(1)
    if inp == ord("q"):
        cv2.destroyAllWindows()
        break
    elif inp == ord("c"):
        cv2.imwrite("output.png", final_img)