# -*- coding:utf-8 -*-
from screen_processor import MapleScreenCapturer
import cv2, time, imutils
import numpy as np
cap = MapleScreenCapturer()
from win32gui import SetForegroundWindow
from keras.models import load_model
from keras import backend as K
from tensorflow import Session, ConfigProto, GPUOptions
gpuoptions = GPUOptions(allow_growth=True)
session = Session(config=ConfigProto(gpu_options=gpuoptions))
K.set_session(session)
model = load_model("arrow_classifier_keras.h5")
#model.compile(optimizer = "adam", loss = 'categorical_crossentropy', metrics = ['accuracy'])
from keras.models import load_model
x, y, w, h = 450, 180, 500, 130
clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(8,8))
ds = None
while True:
    img = cap.capture(set_focus=False)
    img_arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    final_img = imutils.resize(img_arr, width = 200)
    cv2.imshow("s to save image", final_img)
    inp = cv2.waitKey(1)
    if inp == ord("q"):
        cv2.destroyAllWindows()
        break
    elif inp == ord("d"):
        SetForegroundWindow(cap.ms_get_screen_hwnd())
        time.sleep(0.3)
        ds = cap.capture(set_focus=False)
        ds = cv2.cvtColor(np.array(ds), cv2.COLOR_RGB2BGR)
        ds = ds[y:y + h, x:x + w]

img = ds
color = img.copy()
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
l, a, b = cv2.split(lab)
l2 = clahe.apply(l)
lab = cv2.merge((l2, a, b))
img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img = cv2.equalizeHist(img)
circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT,1, img.shape[0]/8 , param1=100, param2=30,minRadius=18, maxRadius=30)
circle_roi = []
if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    for (x, y, r) in circles:
        print(x, y, r)
        cropped = color[max(0,int(y-60/2)):int(y+60/2), max(0,int(x-60/2)):int(x+60/2)]
        circle_roi.append([np.reshape(cropped, [1,60,60,3]), (x,y), cropped])
        cv2.circle(color, (x, y), r, (0, 255, 0), 2)
cv2.imshow("", color)
dt = cv2.waitKey(0)
cv2.destroyAllWindows()


for circ in circle_roi:
    result = np.argmax(model.predict(circ[0]))
    print(result)

    cv2.imshow(str(result), circ[2])
    cv2.waitKeyEx(0)
    cv2.destroyAllWindows()
