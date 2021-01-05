# Copyright(c) Reserved 2020.
# Donghee Lee, University of Seoul
#
__author__ = 'will'

import numpy as np
import cv2

from picamera.array import PiRGBArray
from picamera import PiCamera

#추가 (serial 통신)
import serial
ser = serial.Serial('/dev/serial/by-id/usb-Arduino_Srl_Arduino_Uno_7543134333435161E1E1-if00',9600)

class RC_Car_Interface():

    def __init__(self):
        self.left_wheel = 0
        self.right_wheel = 0
        self.camera = PiCamera()
        self.camera.resolution = (320,320)         # set camera resolution to (320, 320)
        self.camera.color_effects = (128,128)      # set camera to black and white

    def finish_iteration(self):
        print('finish iteration')

    def set_right_speed(self, speed):
        #print('set right speed to ', speed)
        cmd = ("R%d\n" % speed).encode('ascii')
        print("My cmd is %s" % cmd)
        ser.write(cmd)
    
    def set_left_speed(self, speed):
        #print('set left speed to ', speed)
        cmd = ("L%d\n" % speed).encode('ascii')
        print("My cmd is %s" % cmd)
        ser.write(cmd)
        
    # set_stop_speed 추가
    def set_stop_speed(self):
        cmd = ("S%d\n" % 0).encode('ascii')
        print("My cmd is %s" % cmd)
        ser.write(cmd)
        
    def get_image_from_camera(self):
        img = np.empty((320, 320, 3), dtype=np.uint8)
        self.camera.capture(img, 'bgr')
        
        img = img[:,:,0]           # 3 dimensions have the same value because camera is set to black and white
                                   # remove two dimension data
#        print(img)
        
        threshold = int(np.mean(img))*0.5
#        print(threshold)

        # Invert black and white with threshold
        ret, img2 = cv2.threshold(img.astype(np.uint8), threshold, 255, cv2.THRESH_BINARY_INV)

        img2 = cv2.resize(img2,(16,16), interpolation=cv2.INTER_AREA )
        
        #180도 회전 추가
        img2 = cv2.rotate(img2, cv2.ROTATE_180)
#        cv2.imshow("Image", img2)
#        cv2.waitKey(0)
        return img2

    def stop(self):     # robot stop
        print('stop')

# Test Only
#RC_Car_Interface().get_image_from_camera()