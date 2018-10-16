# -*- coding:utf-8 -*-
from screen_processor import MapleScreenCapturer
import cv2
import numpy as np
cap = MapleScreenCapturer()

while True:
    img = cap.capture(set_focus=False)
    grayscale = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(grayscale, (7,7), 3)
    eroded = cv2.erode(blurred, (7,7))
    #dilated = cv2.dilate(eroded, (7,7))
    canny = cv2.Canny(eroded, threshold1=180, threshold2=255)
    cv2.imshow("", canny)

    inp = cv2.waitKey(1)
    if inp == ord("q"):
        cv2.destroyAllWindows()
        break