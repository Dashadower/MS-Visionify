# -*- coding:utf-8 -*-
import sys
sys.path.append("../src")
from screen_processor import MapleScreenCapturer
import cv2, time, imutils
import numpy as np
cap = MapleScreenCapturer()
from win32gui import SetForegroundWindow
from keras.models import load_model
from keras import backend as K
from tensorflow import Session, ConfigProto, GPUOptions
# Use GPU Mode TF
"""gpuoptions = GPUOptions(allow_growth=True)
session = Session(config=ConfigProto(gpu_options=gpuoptions))
K.set_session(session)
# End Use GPU Mode TF
"""
model = load_model("arrow_classifier_keras_gray.h5")
model.compile(optimizer = "adam", loss = 'categorical_crossentropy', metrics = ['accuracy'])
model.load_weights("arrow_classifier_keras_gray.h5")


x, y, w, h = 450, 180, 500, 130
ds = None
while True:
    img = cap.capture(set_focus=False)
    img_arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    final_img = imutils.resize(img_arr, width = 200)
    cv2.imshow("s to save image", final_img)
    inp = cv2.waitKey(1)

    if inp == ord("q"):
        SetForegroundWindow(cap.ms_get_screen_hwnd())
        time.sleep(0.3)
        ds = cap.capture(set_focus=False)
        ds = cv2.cvtColor(np.array(ds), cv2.COLOR_RGB2BGR)
        ds = ds[y:y + h, x:x + w]
        print("saved")
        cv2.destroyAllWindows()
        break


display = ds.copy()
gray = display.copy()
gray = cv2.cvtColor(gray, cv2.COLOR_BGR2HSV)
# Maximize saturation
gray[:, :, 1] = 255
gray[:, :, 2] = 255
gray = cv2.cvtColor(gray, cv2.COLOR_HSV2BGR)
gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)

circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,1, gray.shape[0]/8 , param1=100, param2=30,minRadius=18, maxRadius=30)
circle_roi = []
if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    for (x, y, r) in circles:
        print(x, y, r)
        cropped = gray[max(0,int(y-60/2)):int(y+60/2), max(0,int(x-60/2)):int(x+60/2)]
        cv2.imwrite("validation_data/%d%d%d.png" % (x, y, r), cropped)
        circle_roi.append([np.reshape(cropped, [1,60,60,1]), (x,y), cropped])

        cv2.circle(gray, (x, y), r, (0, 255, 0), 2)
        cv2.circle(display, (x, y), r, (0, 255, 0), 2)

cv2.imshow("", display)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imshow("", gray)
cv2.waitKey(0)
cv2.destroyAllWindows()
circle_roi = sorted(circle_roi, key=lambda x: x[1][0])
labels = {'down': 0, 'left': 1, 'right': 2, 'up': 3}
img2tensor = np.vstack([x[0] for x in circle_roi])
res = model.predict(img2tensor, batch_size=4)
index = 0
for result in res:
    final_class = np.argmax(result, axis=-1)
    for key, val in labels.items():
        if final_class == val:
            print(key)

    cv2.imshow(str(result), circle_roi[index][2])

    cv2.waitKeyEx(0)
    cv2.destroyAllWindows()
    index += 1
