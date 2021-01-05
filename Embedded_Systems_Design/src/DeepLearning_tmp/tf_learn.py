# Copyright Reserved (2020).
# Donghee Lee, Univ. of Seoul
#
__author__ = 'will'

from keras.models import Sequential
from keras.layers import Dense
#from sklearn.model_selection import train_test_split

import numpy as np
#import pandas as pd
import tensorflow as tf
#import pickle
from get_image_data import *

class DNN_Driver():
    def __init__(self):
        self.trX = None
        self.trY = None
        self.teX = None
        self.teY = None
        self.model = None

    def tf_learn(self):
        self.trX, self.trY = get_training_data()
        self.teX, self.teY = get_test_data()

        seed = 0
        np.random.seed(seed)
        tf.random.set_seed(seed)

        self.model=Sequential()
        self.model.add(Dense(512, input_dim=np.shape(self.trX)[1], activation='relu'))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(1))

        self.model.compile(loss='mean_squared_error', optimizer='adam')

        self.model.fit(self.trX, self.trY, epochs=6, batch_size=1)
        
        # 확인용으로 넣은 코드 start
        Y_prediction = self.model.predict(self.teX).flatten()
        for i in range(len(self.teY)):
            label = self.teY[i]
            pred = Y_prediction[i]
            print("label:{:.2f}, pred:{:.2f}".format(label, pred))
        # end
        return

    def predict_direction(self, img):
        print(img.shape)
        #img = np.array([np.reshape(img,img.shape**2)]) # 이거 원래 주석처리 되어있었음 & np.reshape~이 []로 묶여있었음
        #img = np.reshape(img,img.shape**2)
        ret =  self.model.predict(np.array([img]))
        return ret

    def get_test_img(self):
        img = self.teX[10]
        return img

        