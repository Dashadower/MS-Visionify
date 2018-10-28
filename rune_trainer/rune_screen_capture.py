# -*- coding:utf-8 -*-
from screen_processor import MapleScreenCapturer
from keystate_manager import KeyboardInputManager
from directinput_constants import DIK_SPACE, DIK_UP
import cv2, os, time, glob, imutils
import numpy as np
cap = MapleScreenCapturer()
kbd = KeyboardInputManager()
from win32gui import SetForegroundWindow
os.chdir("images/screenshots/finished")
imgs = glob.glob("*.png")
highest = 0
for name in imgs:
    order = int(name[6:].split(".")[0])
    highest = max(order, highest)

os.chdir("../")
x, y, w, h = 450, 180, 500, 130
while True:
    img = cap.capture(set_focus=False)
    img_arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    final_img = imutils.resize(img_arr, width = 200)
    cv2.imshow("s to save image", final_img)
    inp = cv2.waitKey(1)
    if inp == ord("q"):
        cv2.destroyAllWindows()
        break
    elif inp == ord("s"):
        SetForegroundWindow(cap.ms_get_screen_hwnd())
        for t in range(5):
            time.sleep(1)
            kbd.single_press(DIK_SPACE)
            time.sleep(0.3)
            ds = cap.capture(set_focus=False)
            ds = cv2.cvtColor(np.array(ds), cv2.COLOR_RGB2BGR)
            ds = ds[y:y+h, x:x+w]

            highest = highest + 1
            cv2.imwrite("output%d.png"%(highest), ds)
            print("saved", "output%d.png"%(highest))
            for g in range(3):
                kbd.single_press(DIK_UP)
                time.sleep(0.2)
            time.sleep(3)
        print("done")
    elif inp == ord("d"):
        SetForegroundWindow(cap.ms_get_screen_hwnd())
        time.sleep(0.3)
        ds = cap.capture(set_focus=False)
        ds = cv2.cvtColor(np.array(ds), cv2.COLOR_RGB2BGR)
        ds = ds[y:y + h, x:x + w]

        highest = highest + 1
        cv2.imwrite("output%d.png" % (highest), ds)
        print("saved", "output%d.png" % (highest))