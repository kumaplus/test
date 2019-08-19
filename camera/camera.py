# -*- coding: utf-8 -*-
from time import sleep
import smbus
import math

def resetPCA9685():
    bus.write_byte_data(address_pca9685, 0x00, 0x00)

def setPCA9685Freq(freq):
    freq = 0.9*freq # Arduinoのライブラリより
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    prescale = int(math.floor(prescaleval + 0.5))
    oldmode = bus.read_byte_data(address_pca9685, 0x00)
    newmode = (oldmode & 0x7F) | 0x10             # スリープモード
    bus.write_byte_data(address_pca9685, 0x00, newmode) # スリープモードへ
    bus.write_byte_data(address_pca9685, 0xFE, prescale) # プリスケーラーをセット
    bus.write_byte_data(address_pca9685, 0x00, oldmode)
    sleep(0.005)
    bus.write_byte_data(address_pca9685, 0x00, oldmode | 0xa1)

def setPCA9685Duty(channel, on, off):
    channelpos = 0x6 + 4*channel
    try:
        bus.write_i2c_block_data(address_pca9685, channelpos, [on&0xFF, on>>8, off&0xFF, off>>8] )
    except IOError:
        pass

def move2(val0, val1, val2, val3):
    global RTLT
    global UPDWN
    global UPDWN2
    global RTLT2
    
    out0 = int(276 + val0 * 1.48)
    out1 = int(276 - val1 * 1.48)
    out2 = int(276 - val2 * 1.48)
    out3 = int(276 + val3 * 1.48)
    dif0 = out0 - RTLT 
    dif1 = out1 - UPDWN
    dif2 = out2 - UPDWN2
    dif3 = out3 - RTLT2
    tmp0 = RTLT + int(dif0 / 2)  
    tmp1 = UPDWN + int(dif1 / 2)
    tmp2 = UPDWN2 + int(dif2 / 2)
    tmp3 = RTLT2 + int(dif3 / 2)
    setPCA9685Duty(0, 0, tmp0)
    setPCA9685Duty(1, 0, tmp1)
    setPCA9685Duty(2, 0, tmp2)
    setPCA9685Duty(3, 0, tmp3)
    sleep(1)
    setPCA9685Duty(0, 0, out0)
    setPCA9685Duty(1, 0, out1)
    setPCA9685Duty(2, 0, out2)
    setPCA9685Duty(3, 0, out3)
    sleep(1)
    RTLT = out0
    UPDWN = out1
    UPDWN2 = out2
    RTLT2 = out3

def move(val0, val1, val2, val3):
    global RTLT
    global UPDWN
    global UPDWN2
    global RTLT2
 
    out0 = int(276 + val0 * 1.48)
    out1 = int(276 - val1 * 1.48)
    out2 = int(276 - val2 * 1.48)
    out3 = int(276 + val3 * 1.48)
    dif0 = out0 - RTLT 
    dif1 = out1 - UPDWN
    dif2 = out2 - UPDWN2
    dif3 = out3 - RTLT2 

    for i in range(10):
        tmp0 = RTLT + int(dif0 * math.sin(math.radians(i) * 10))  
        tmp1 = UPDWN + int(dif1 * math.sin(math.radians(i) * 10))
        tmp2 = UPDWN2 + int(dif2 * math.sin(math.radians(i) * 10))
        tmp3 = RTLT2 + int(dif3 * math.sin(math.radians(i) * 10))
        setPCA9685Duty(0, 0, tmp0)
        setPCA9685Duty(1, 0, tmp1)
        setPCA9685Duty(2, 0, tmp2)
        setPCA9685Duty(3, 0, tmp3)
        sleep(0.1)
    RTLT = out0
    UPDWN = out1
    UPDWN2 = out2
    RTLT2 = out3
    sleep(1)

def reading(sensor,trig,echo):
    import time
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)

    GPIO.setmode(GPIO.BCM)

    if sensor == 0:
        GPIO.setup(trig,GPIO.OUT)
        GPIO.setup(echo,GPIO.IN)
        GPIO.output(trig, GPIO.LOW)
        time.sleep(0.3)

        GPIO.output(trig, True)
        time.sleep(0.00001)
        GPIO.output(trig, False)

        while GPIO.input(echo) == 0:
          signaloff = time.time()

        while GPIO.input(echo) == 1:
          signalon = time.time()

        timepassed = signalon - signaloff
        distance = timepassed * 17000
        return distance
        GPIO.cleanup()
    else:
        print "Incorrect usonic() function varible."

def calc_deg(distance):
    if distance > 20:
        t1 = 0
        t2 = 0  
    else:
        distance = distance +4
        t1 = math.degrees(math.acos((distance/2)/10.5))
        t2 = 180 - (90 + t1) 
        t1 = int(t1 - 90)
        if t2 < 90:
            t2 = -1 * int(90 - 2*t2)
        else:
            t2 = int(2*d5 - 90)
    return [t1,t2]

bus = smbus.SMBus(1)
address_pca9685 = 0x40

resetPCA9685()
setPCA9685Freq(50)

UPDWN = 276
RTLT = 276 
UPDWN2 = 276
RTLT2 = 276

move(0, 0, 0, 0)
sleep(1)

try:
    pos = 10 
    move(pos, 0, 0, 0)
    sleep(1)
    print reading(0, 17, 21)
    print calc_deg(reading(0, 17, 21))
    set1, set2 = calc_deg(reading(0, 17, 21))
    move(pos, set1, set2, 90)
    sleep(1)
    move(pos, set1, set2, 0)
    sleep(1)
    move(0, 0, 0, 0)
except KeyboardInterrupt:
    pass
