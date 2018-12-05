# -*- coding:utf-8 -*-
"""Classifier model verifier"""
import sys
sys.path.append("../src")

from screen_processor import MapleScreenCapturer
import cv2, time, imutils, os, glob, random
import numpy as np
from win32gui import SetForegroundWindow
from keras.models import load_model

cap = MapleScreenCapturer()

from keras import backend as K
from tensorflow import Session, ConfigProto, GPUOptions
# Use GPU Mode TF
"""gpuoptions = GPUOptions(allow_growth=True)
session = Session(config=ConfigProto(gpu_options=gpuoptions))
K.set_session(session)
# End Use GPU Mode TF
"""
model_name = "arrow_classifier_keras_gray.h5"
model = load_model(model_name)
model.compile(optimizer = "adam", loss = 'categorical_crossentropy', metrics = ['accuracy'])
model.load_weights(model_name)

labels = {'down': 0, 'left': 1, 'right': 2, 'up': 3}

mode = input("{0} validator\n1 to test from validation_data\n2 to run data capture tool\n>".format(model_name))
if mode == str(1):

    os.chdir("images/cropped/validation_data")
    _images = glob.glob("*.png")
    random.shuffle(_images)
    images = []
    for x in range(4):
        images.append(cv2.imread(os.path.join(os.getcwd(), _images[x]), cv2.IMREAD_GRAYSCALE))
        print(os.path.join(os.getcwd(), _images[x]))
    img2tensor = np.vstack([np.reshape(x, [1,60,60,1]) for x in images])
    res = model.predict(img2tensor, batch_size=4)
    index = 0
    for result in res:
        final_class = np.argmax(result, axis=-1)
        for key, val in labels.items():
            if final_class == val:
                print(key)

        cv2.imshow(str(result), images[index])
        cv2.waitKeyEx(0)
        cv2.destroyAllWindows()

elif mode == str(2):
    x, y, w, h = 450, 180, 500, 130
    ds = None
    while True:
        img = cap.capture(set_focus=False)
        img_arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img_arr = img_arr[y:y + h, x:x + w]
        final_img = imutils.resize(img_arr, width = 200)
        cv2.imshow("q to save image", final_img)
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
    os.chdir("images/cropped/validation_data")
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            print(x, y, r)
            cropped = gray[max(0,int(y-60/2)):int(y+60/2), max(0,int(x-60/2)):int(x+60/2)]
            cv2.imwrite("%d%d%d.png" % (x, y, r), cropped)
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
