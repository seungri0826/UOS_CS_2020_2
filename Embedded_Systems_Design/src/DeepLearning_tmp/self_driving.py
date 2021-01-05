# Copyright Reserved (2020).
# Donghee Lee, Univ. of Seoul
#
__author__ = 'will'

from rc_car_interface import RC_Car_Interface
from tf_learn import DNN_Driver
import numpy as np
import time
import cv2

class SelfDriving:

    def __init__(self):
        self.rc_car_cntl = RC_Car_Interface()
        self.dnn_driver = DNN_Driver()

        self.rc_car_cntl.set_left_speed(0)
        self.rc_car_cntl.set_right_speed(0)
    
        self.velocity = 0
        self.direction = 0
    
        self.dnn_driver.tf_learn()
    
    def rc_car_control(self, direction):
        #calculate left and right wheel speed with direction
        if direction < -1.0:
            direction = -1.0
        if direction > 1.0:
            direction = 1.0
            
        # (1) 직진
        if direction <= 0.25 and direction >= -0.25:
            self.rc_car_cntl.set_left_speed(40)
            self.rc_car_cntl.set_right_speed(40)
            
        # (2) 좌회전
        elif direction < 0:
            if direction >= -0.37:
                self.rc_car_cntl.set_left_speed(0)
                self.rc_car_cntl.set_right_speed(41)
            elif direction >= -0.49:
                self.rc_car_cntl.set_left_speed(0)
                self.rc_car_cntl.set_right_speed(42)
            elif direction >= -0.61:
                self.rc_car_cntl.set_left_speed(0)
                self.rc_car_cntl.set_right_speed(43)
            elif direction >= -0.73:
                self.rc_car_cntl.set_left_speed(0)
                self.rc_car_cntl.set_right_speed(44)
            elif direction >= -0.85:
                self.rc_car_cntl.set_left_speed(0)
                self.rc_car_cntl.set_right_speed(45)
            else:
                self.rc_car_cntl.set_left_speed(-20)
                self.rc_car_cntl.set_right_speed(40)
                
        # (3) 우회전
        else:
            if direction <= 0.37:
                self.rc_car_cntl.set_right_speed(0)
                self.rc_car_cntl.set_left_speed(41)
            elif direction <= 0.49:
                self.rc_car_cntl.set_right_speed(0)
                self.rc_car_cntl.set_left_speed(42)
            elif direction <= 0.61:
                self.rc_car_cntl.set_right_speed(0)
                self.rc_car_cntl.set_left_speed(43)
            elif direction <= 0.73:
                self.rc_car_cntl.set_right_speed(0)
                self.rc_car_cntl.set_left_speed(44)
            elif direction <= 0.85:
                self.rc_car_cntl.set_right_speed(0)
                self.rc_car_cntl.set_left_speed(45)
            else:
                self.rc_car_cntl.set_right_speed(-20)
                self.rc_car_cntl.set_left_speed(40)
                
        self.rc_car_cntl.set_stop_speed()
        #추가
        '''
        if direction == 0.02:
            left_speed = 1.0
            right_speed = 1.0
            self.rc_car_cntl.set_right_speed(95*right_speed)
        elif direction == -0.02:
            left_speed = 1.0
            right_speed = 1.0
            self.rc_car_cntl.set_left_speed(95*left_speed)
        '''
        #추가 끝
        #turn left
        #if direction < 0.0:
            #left_speed = 1.0+direction
            #right_speed = 1.0
            #self.rc_car_cntl.set_left_speed(95*left_speed)
        #turn right
        #else:
            #right_speed = 1.0-direction
            #left_speed = 1.0
            #self.rc_car_cntl.set_right_speed(95*right_speed) 

        #self.rc_car_cntl.set_right_speed(92*right_speed) 
        #self.rc_car_cntl.set_left_speed(92*left_speed)
        # 추가
        #time.sleep(0.1)
        #self.rc_car_cntl.set_right_speed(0) 
        #self.rc_car_cntl.set_left_speed(0)
        #self.rc_car_cntl.set_stop_speed(0)
        #time.sleep(2)

        

    def drive(self):
        while True:

# For test only, get image from DNN test images
#            img from get_test_img() returns [256] array. Do not call np.reshape()
#            img = self.dnn_driver.get_test_img()
#            direction = self.dnn_driver.predict_direction(img)

            img = self.rc_car_cntl.get_image_from_camera()
# predict_direction wants [256] array, not [16,16]. Thus call np.reshape to convert [16,16] to [256] array
            img = np.reshape(img,img.shape[0]**2)

            direction = self.dnn_driver.predict_direction(img)         # predict with single image
            print(direction[0][0])
            self.rc_car_control(direction[0][0])

            # For debugging, show image
            #cv2.imshow("target",  cv2.resize(img, (280, 280)) )
            cv2.imshow("target",  cv2.resize(img, (16, 16)) )
            cv2.waitKey(500)

            #time.sleep(0.001) # 원래 이거임!
            time.sleep(0.001)

        self.rc_car_cntl.stop()
        cv2.destroyAllWindows()

SelfDriving().drive()
