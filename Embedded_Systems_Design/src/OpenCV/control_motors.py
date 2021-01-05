import time
import serial
ser = serial.Serial('/dev/serial/by-id/usb-Arduino_Srl_Arduino_Uno_7543134333435161E1E1-if00',9600)

#SPEED = 10
'''
def MotorsSetup():
    cmd_L = ("L%d\n" % 0).encode('ascii')
    cmd_R = ("R%d\n" % 0).encode('ascii')
    print("My cmd is %s" % cmd_R)
    ser.write(cmd_R)
    ser.write(cmd_L)
'''
def Set_Speed(Lspeed, Rspeed):
    if Lspeed < 0:
        cmd_L =("L-%2d" % abs(Lspeed))
    else:
        cmd_L = ("L+%2d" % Lspeed)
    if Rspeed < 0:
        cmd_R = ("R-%2d\n" % abs(Lspeed))
    else:
        cmd_R = ("R+%2d\n" % Rspeed)
    cmd = (cmd_L + cmd_R).encode('ascii')
    print("My cmd is %s" % cmd)
    ser.write(cmd)
    
    
def L_Speed(speed):
    cmd_L = ("L%d\n" % speed).encode('ascii')
    print("My cmd is %s" % cmd_L)
    ser.write(cmd_L)

def R_Speed(speed):
    cmd_R = ("R%d\n" % speed).encode('ascii')
    print("My cmd is %s" % cmd_R)
    ser.write(cmd_R)
'''
def Direction(difference):
    difference /= 2
    #difference /= 1.5
    if difference < 0:
        L_Speed(SPEED+difference)
        R_Speed(SPEED-difference/2)
    else:
        L_Speed(SPEED+difference/2)
        R_Speed(SPEED-difference)
    #L_Speed(SPEED+difference)
    #R_Speed(SPEED-difference)
    time.sleep(0.3)
    MotorsStop()
    

def BaseSpeed(speed):
    global SPEED
    SPEED = speed
    L_Speed(SPEED)
    R_Speed(SPEED)

def GetSpeed():
    global SPEED
    return SPEED
'''
def MotorsStop():
    #cmd_L = ("L%d\n" % 0).encode('ascii')
    #cmd_R = ("R%d\n" % 0).encode('ascii')
    #print("My cmd is %s" % cmd_R)
    #ser.write(cmd_R)
    #ser.write(cmd_L)
    cmd = ("S%d\n" % 0).encode('ascii')
    print("My cmd is %s" % cmd)
    ser.write(cmd)
    #time.sleep(5)
