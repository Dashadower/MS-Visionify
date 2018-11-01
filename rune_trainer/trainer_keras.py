
# -*- coding:utf-8 -*-
import cv2
import numpy as np
import os
from random import shuffle
import glob


train_dir = "images\\cropped\\traindata"
test_dir = "images\\cropped\\testdata"
MODEL_NAME = "ARROWS.model"

img_size = 60


# Importing the Keras libraries and packages
from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Activation
from keras.layers import BatchNormalization
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import adam

from keras import backend as K
from tensorflow import Session, ConfigProto, GPUOptions
gpuoptions = GPUOptions(allow_growth=True)
session = Session(config=ConfigProto(gpu_options=gpuoptions))
K.set_session(session)
classifier = Sequential()

classifier.add(Conv2D(32, (3,3), input_shape=(img_size, img_size, 1)))
classifier.add(Activation("relu"))
classifier.add(BatchNormalization(axis=-1))


classifier.add(Conv2D(64, (3,3), padding='same'))
classifier.add(Activation("relu"))
classifier.add(BatchNormalization(axis=-1))
#classifier.add(Conv2D(64, (3, 3), padding='same'))
#classifier.add(Activation("relu"))
#classifier.add(BatchNormalization(axis=-1))
classifier.add(MaxPooling2D(pool_size=(2, 2)))
#classifier.add(Dropout(0.25))

classifier.add(Conv2D(32, (3,3), input_shape=(img_size, img_size, 1)))
classifier.add(Activation("relu"))
classifier.add(BatchNormalization(axis=-1))


classifier.add(Conv2D(64, (3,3), padding='same'))
classifier.add(Activation("relu"))
classifier.add(BatchNormalization(axis=-1))
#classifier.add(Conv2D(64, (3, 3), padding='same'))
#classifier.add(Activation("relu"))
#classifier.add(BatchNormalization(axis=-1))
classifier.add(MaxPooling2D(pool_size=(2, 2)))
classifier.add(Dropout(0.25))


classifier.add(Flatten())
classifier.add(Dense(128))
classifier.add(Activation("relu"))
classifier.add(BatchNormalization())
classifier.add(Dropout(0.5))


classifier.add(Dense(4))
classifier.add(Activation("softmax"))


classifier.compile(optimizer = adam(lr=1e-5), loss = 'categorical_crossentropy', metrics = ['accuracy'])

train_datagen = ImageDataGenerator(rotation_range=12)

test_datagen = ImageDataGenerator(rotation_range=12)

training_set = train_datagen.flow_from_directory('images/cropped/traindata',
                                                 color_mode="grayscale",
                                                 target_size = (img_size, img_size),
                                                 batch_size = 32,
                                                 class_mode = 'categorical', shuffle=True)

test_set = test_datagen.flow_from_directory('images/cropped/testdata',
                                            color_mode="grayscale",
                                            target_size = (img_size, img_size),
                                            batch_size = 32,
                                            class_mode = 'categorical', shuffle=True)

with open("class_indices.txt", "w") as indices_fine:
    indices_fine.write(str(classifier.summary()))
    indices_fine.write("\n")
    indices_fine.write("training_set indices:\n"+str(training_set.class_indices))
    indices_fine.write("test_set indices:\n"+str(test_set.class_indices))

classifier.fit_generator(training_set,steps_per_epoch = 8000,epochs = 15,validation_data = test_set,validation_steps = 2000, shuffle=True)

classifier.save("arrow_classifier_keras_gray.h5")