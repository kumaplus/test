# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import smbus
import math
from time import sleep
import csv
import os

#os.remove("data.csv")

GPIO.setmode(GPIO.BCM)

GPIO.setup(25, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
p0 = GPIO.PWM(25, 50)
p1 = GPIO.PWM(24, 50)
p2 = GPIO.PWM(23, 50)
p3 = GPIO.PWM(22, 50)
p0.start(0)
p1.start(0)
p2.start(0)
p3.start(0)

DEV_ADDR = 0x68

ACCEL_XOUT = 0x3b
ACCEL_YOUT = 0x3d
ACCEL_ZOUT = 0x3f
TEMP_OUT = 0x41
GYRO_XOUT = 0x43
GYRO_YOUT = 0x45
GYRO_ZOUT = 0x47

PWR_MGMT_1 = 0x6b
PWR_MGMT_2 = 0x6c   

countS = 0
recOmegaI = []
omegaI = 0
thetaI = 0
sumPower = 0
sumSumP = 0
#kAngle = 50 
#kOmega = 500 
#kSpeed = 60 
#kDistance = 20 
kAngle = 50 
kOmega = 500 
kSpeed = 60 
kDistance = 20 
powerScale = 0
power = 0
vE5 = 0
xE5 = 0
SEN_CNT = 15 
MTR = 70 

bus = smbus.SMBus(1)
bus.write_byte_data(DEV_ADDR, PWR_MGMT_1, 0)


def read_word(adr):
    try:
        high = bus.read_byte_data(DEV_ADDR, adr)
        low = bus.read_byte_data(DEV_ADDR, adr+1)
        val = (high << 8) + low
    except IOError:
        print("IOError")
        val = 0
        pass
    
    return val

# Sensor data read
def read_word_sensor(adr):
    val = read_word(adr)
    if (val >= 0x8000):         # minus
        return -((65535 - val) + 1)
    else:                       # plus
        return val

def get_temp():
    temp = read_word_sensor(TEMP_OUT)
    x = temp / 340 + 36.53      # data sheet(register map)記載の計算式.
    return x

def getGyro():
    x = read_word_sensor(GYRO_XOUT)/ 131.0
    y = read_word_sensor(GYRO_YOUT)/ 131.0
    z = read_word_sensor(GYRO_ZOUT)/ 131.0
    return [x, y, z]

def getAccel():
    x = read_word_sensor(ACCEL_XOUT)/ 16384.0
    y= read_word_sensor(ACCEL_YOUT)/ 16384.0
    z= read_word_sensor(ACCEL_ZOUT)/ 16384.0
    return [x, y, z]

def calc_slope_for_accel_2axis_deg(x, y, z): # degree
    #
    # θ = atan(X軸出力加速度[g]/Y軸出力加速度[g])
    #
    slope_xy = math.atan( x / y )
    deg_xy = math.degrees( slope_xy )
    if x > 0 and y > 0:    # 第1象限(0°〜+90°).
        deg_xy = deg_xy
    if x > 0 and y < 0:    # 第2象限(+90°〜±180°).
        deg_xy += 180.0
    if x < 0 and y < 0:    # 第3象限(±180°〜-90°).
        deg_xy -= 180.0
    if x < 0 and y > 0:    # 第4象限(-90°〜0°).
        deg_xy = deg_xy
    return deg_xy

def calc_slope_for_accel_3axis_deg(x, y, z): # degree
    # θ（シータ）
    theta = math.atan( x / math.sqrt( y*y + z*z ) )
    # Ψ（プサイ）
    psi = math.atan( y / math.sqrt( x*x + z*z ) )
    # Φ（ファイ）
    phi = math.atan( math.sqrt( x*x + y*y ) / z )

    deg_theta = math.degrees( theta )
    deg_psi   = math.degrees( psi )
    deg_phi   = math.degrees( phi )
    return [deg_theta, deg_psi, deg_phi]

def setup():
    global recOmegaI

    for i in range(10):
        recOmegaI.append(0)
     
def write_csv(list):
    with open('data.csv', 'a') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(list)

def chkAndCtl():
    global recOmegaI
    global thetaI
    global omegaI
    global countS
    global vE5
    global xE5
    global sumPower
    global sumSumP
    global power

    R = 0;
    for i in range(SEN_CNT):
        gx, gy, gz = getGyro()
        #print 'gyro[deg/s]',
        #print 'x: %08.3f' % gx,
        #print 'y: %08.3f' % gy,
        #print 'z: %08.3f' % gz,
        #print
        R = R + gy 
        #sleep(0.09)  
    omegaI = R / SEN_CNT 
    print("omegaI: " + str(omegaI))
    if abs(omegaI) < 2:
        omegaI = 0
    recOmegaI[0] = omegaI
    thetaI = thetaI + omegaI
    countS = 0
    for i in range(10):
        if abs(recOmegaI[i]) < 4:
            countS += 1

    if countS > 9:
        thetaI = 0 
        vE5 = 0
        xE5 = 0
        sumPower = 0
        sumSumP = 0
    
    for i in reversed(range(1,10)):
        recOmegaI[i] = recOmegaI[i-1]

    powerScale = (kAngle * thetaI / 100) + (kOmega * omegaI / 100) 
    tmp = (kSpeed * vE5 / 1000) + (kDistance * xE5 / 1000)
    powerScale += tmp
    #power = max(min(95 * powerScale / 100, 255), -255)
    power = max(min(95 * powerScale / 100, MTR), MTR * -1)
    print 'power: %08.3f' % power 
    sumPower = sumPower + power
    sumSumP = sumSumP + sumPower
    vE5 = sumPower
    xE5 = sumSumP / 1000 

def move_forward(val):
    p1.ChangeDutyCycle(0)
    p0.ChangeDutyCycle(val)

    p3.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(val)

def move_back(val):
    p0.ChangeDutyCycle(0)
    p1.ChangeDutyCycle(val)

    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(val)
 
try:
    setup()

    while 1:
        chkAndCtl()
        if power > 0:
            print("back")
            move_back(power)
        else:
            print("forward")
            move_forward(abs(power)) 

except KeyboardInterrupt:
    pass

p0.stop()
p1.stop()
p2.stop()
p3.stop()
GPIO.cleanup()
