import serial
ser = serial.Serial('/dev/serial/by-id/usb-Arduino_Srl_Arduino_Uno_7543134333435161E1E1-if00',9600)

#speed = 0 # speed 처음부터 지정해봄
speed = 10
#if ser is None:
#    ser = serial.Serial('/dev/ttyUSB1',9600)
while True:
    #cmd = ("R%d\n" % speed).encode('ascii')
    cmd = ("L%d\n" % speed).encode('ascii')
    print("My cmd is %s" % cmd)
    ser.write(cmd)
#   For debugging, read cmd from arduino    
    read_serial=ser.readline()
    print (read_serial)
    #speed = speed + 1  # 주석처리함