# -*- coding: utf-8 -*-
import socket
import sys
import os
import numpy as np
import pdb

import cv2
import time

from Image import *
from Utils import *
from control_motors import *

font = cv2.FONT_HERSHEY_SIMPLEX
direction = 0

#N_SLICES만큼 이미지를 조각내서 Images[] 배열에 담는다
Images=[]
N_SLICES = 3
middleX = 320 # 추가

for q in range(N_SLICES):
    Images.append(Image())

### 카메라로 추가
video_capture = cv2.VideoCapture(-1)
video_capture.set(3, 640)
video_capture.set(4, 240)

while(True):

    # Capture the frames
    ret, frame = video_capture.read()
    
    # 추가) 180도 회전
    frame = cv2.rotate(frame, cv2.ROTATE_180)

    # Crop the image
    crop_img = frame#[60:120, 0:160]

    # Convert to grayscale
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    # Gaussian blur
    blur = cv2.GaussianBlur(gray,(5,5),0)

    # Color thresholding
    ret,thresh1 = cv2.threshold(blur,50,255,cv2.THRESH_BINARY_INV) # 60
    
    cv2.imshow("1", thresh1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
            
    # 추가
    crop_img = RemoveBackground(crop_img, False)
    #cv2.imshow("2", crop_img)
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break
    if crop_img is not None:
        #이미지를 조각내서 윤곽선을 표시하게 무게중심 점을 얻는다
        Points = SlicePart(crop_img, Images, N_SLICES)
        print('Points : ', Points)

        #N_SLICES 개의 무게중심 점을 x좌표, y좌표끼리 나눈다
        #x = Points[::2]
        #y = Points[1::2]
    
        # for debugging
        #print(x)
        #print(y)
        
        ##### 모터 제어 코드 (middleX - Points[2][0]) 값에 따라
        toFollow = middleX - Points[2][0] #[2][0]이랑 [1][0] 평균값으로?
        # (1) -20 ~ 20일 때 = 직진
        if toFollow <= 20 and toFollow >= -20:
            L_Speed(40)
            R_Speed(40)
            #MotorsStop()
        # (2) 음수일 때 = 우회전
        elif toFollow < 0:
            if toFollow >= -70:
                R_Speed(0)
                L_Speed(41)
                #MotorsStop()
            elif toFollow >= -120:
                R_Speed(0)
                L_Speed(42)
                #MotorsStop()
            elif toFollow >= -170:
                R_Speed(0)
                L_Speed(43)
                #MotorsStop()
            elif toFollow >= -220:
                R_Speed(0)
                L_Speed(44)
                #MotorsStop()
            elif toFollow >= -270:
                R_Speed(0)
                L_Speed(45)
                #MotorsStop()
            else:
                R_Speed(-20) #0
                L_Speed(40) #48
                #MotorsStop()
        # (3) 양수일 때 = 좌회전
        else:
            if toFollow <= 70:
                L_Speed(0)
                R_Speed(41)
                #MotorsStop()
            elif toFollow <= 120:
                L_Speed(0)
                R_Speed(42)
                #MotorsStop()
            elif toFollow <= 170:
                L_Speed(0)
                R_Speed(43)
                #MotorsStop()
            elif toFollow <= 220:
                L_Speed(0)
                R_Speed(44)
                #MotorsStop()
            elif toFollow <= 270:
                L_Speed(0)
                R_Speed(45)
                #MotorsStop()
            else:
                L_Speed(-20) #0
                R_Speed(40) #47
                #MotorsStop()
        #####
        #MotorsStop()
        #조각난 이미지를 한 개로 합친다
        fm = RepackImages(Images)
        
        #완성된 이미지를 표시한다
        cv2.imshow("Vision Race", fm)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print('not even processed')
        
'''
##### while: True
img = cv2.imread('dave.jpg')

if img is not None:
    #이미지를 조각내서 윤곽선을 표시하게 무게중심 점을 얻는다
    Points = SlicePart(img, Images, N_SLICES)
    print('Points : ', Points)

    #N_SLICES 개의 무게중심 점을 x좌표, y좌표끼리 나눈다
    x = Points[::2]
    y = Points[1::2]
    
    # for debugging
    print(x)
    print(y)

    #조각난 이미지를 한 개로 합친다
    fm = RepackImages(Images)
    
    #완성된 이미지를 표시한다
    cv2.imshow("Vision Race", fm)
    if cv2.waitKey(0) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
else:
    print('not even processed')
    '''
##### 
