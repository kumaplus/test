# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import smbus
import math
from time import sleep

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

gCalibrateY = 0
gPowerP = 0
gPowerI = 0
gPowerD = 0

V_MIN = 0
V_MAX = 70

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

def move_stop():
    p0.ChangeDutyCycle(0)
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)

def calc():
    global gPowerI
    ax, ay, az = getAccel()
    gx, gy, gz = getGyro()
    #print 'accel[g]',
    #print 'x: %06.3f' % ax,
    #print 'y: %06.3f' % ay,
    #print 'z: %06.3f' % az,
    #print '||',
    #print 'gyro[deg/s]',
    #print 'x: %08.3f' % gx,
    #print 'y: %08.3f' % gy,
    #print 'z: %08.3f' % gz,
    #print 
    
    if az > 0:    
        theta,psi,phi = calc_slope_for_accel_3axis_deg(ax,ay,az)
        print 'θ=%06.3f' % theta,
        print 'Ψ=%06.3f' % psi,
        print 'Φ=%06.3f' % phi,
        print       # 改行.
    
        gPowerP = (theta - gCalibrateY) / 90
        gPowerI += gPowerP
        gPowerD = gx / 250
        print 'gPowerP=%06.3f' % gPowerP 
        print 'gPowerI=%06.3f' % gPowerI 
        print 'gPowerD=%06.3f' % gPowerD
        print 
        power = gPowerP * 17.0 + gPowerI * 1.5 + gPowerD * 2.0;
        print 'power=%06.3f' % power
        print
        power = max(-1, min(1, power)); 
 
    else:
        power= 0

    return power 

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
    sleep(5)
    ax, ay, az = getAccel()
    theta,psi,phi = calc_slope_for_accel_3axis_deg(ax,ay,az)
   
    gCalibrateY = theta 
    print(gCalibrateY) 
try:
    move_back(70) 
    while 1:
        p = calc()
except KeyboardInterrupt:
    pass

p0.stop()
p1.stop()
p2.stop()
p3.stop()
GPIO.cleanup()
