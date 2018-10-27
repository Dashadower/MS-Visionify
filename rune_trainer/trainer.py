# -*- coding:utf-8 -*-
import cv2
import numpy as np
import os
from random import shuffle
import glob
from tqdm import tqdm

train_dir = "images\\cropped\\traindata"
test_dir = "images\\cropped\\testdata"
MODEL_NAME = "ARROWS.model"
LR = 1e-3
img_size = 60
def create_train_data():
    training_data = []
    os.chdir(train_dir)
    labels = ["up", "down", "left", "right"]
    for label in labels:
        for _img in glob.glob("%s/*.png"%(label)):
            path = _img

            data = cv2.imread(path)
            img = cv2.resize(data,(img_size, img_size))
            if label == "up":
                tlabel = np.array([1,0,0,0])
            elif label == "down":
                tlabel = np.array([0,1,0,0])
            elif label == "left":
                tlabel = np.array([0,0,1,0])
            elif label == "right":
                tlabel = np.array([0,0,0,1])
            training_data.append([np.array(img), tlabel])
    shuffle(training_data)
    os.chdir("../../../")
    np.save("train_data.npy", training_data)
    return training_data

train_data = create_train_data()


import tflearn
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression



convnet = input_data(shape=[None, img_size, img_size, 1], name='input')

convnet = conv_2d(convnet, 32, 2, activation='relu')
convnet = max_pool_2d(convnet, 2)

convnet = conv_2d(convnet, 64, 2, activation='relu')
convnet = max_pool_2d(convnet, 2)

convnet = conv_2d(convnet, 32, 2, activation='relu')
convnet = max_pool_2d(convnet, 2)

convnet = conv_2d(convnet, 64, 2, activation='relu')
convnet = max_pool_2d(convnet, 2)

convnet = conv_2d(convnet, 32, 2, activation='relu')
convnet = max_pool_2d(convnet, 2)

convnet = conv_2d(convnet, 64, 2, activation='relu')
convnet = max_pool_2d(convnet, 2)

convnet = fully_connected(convnet, 1024, activation='relu')
convnet = dropout(convnet, 0.8)

convnet = fully_connected(convnet, 4, activation='softmax')
convnet = regression(convnet, optimizer='adam', learning_rate=LR, loss='categorical_crossentropy', name='targets')

model = tflearn.DNN(convnet, tensorboard_dir="log")

if os.path.exists("%s.meta"%(MODEL_NAME)):
    model.load(MODEL_NAME)
    print("loaded model")


train = train_data[:-200]
test = train_data[-200:]
X = np.array([i[0] for i in train]).reshape(-1, img_size, img_size, 1)
Y = np.array([i[1] for i in train])

test_x = np.array([i[0] for i in test]).reshape(-1, img_size, img_size, 1)
test_y = np.array([i[1] for i in test])

model.fit({'input': X}, {'targets': Y}, n_epoch=5, validation_set=({'input': test_x}, {'targets': test_y}),
    snapshot_step=500, show_metric=True, run_id=MODEL_NAME)