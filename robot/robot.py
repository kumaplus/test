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

def setPCA9685Duty3(channel, on1, off1, on2, off2, on3, off3):
    channelpos = 0x6 + 4*channel
    data = [on1&0xFF, on1>>8, off1&0xFF, off1>>8,
            on2&0xFF, on2>>8, off2&0xFF, off2>>8,
            on3&0xFF, on3>>8, off3&0xFF, off3>>8]
    bus.write_i2c_block_data(address_pca9685, channelpos, data)

def move(i0, i1, i2, i3, i4, i5, i6, i7):
    global UPLLEG
    global DNLLEG
    global WAIST
    global UPRLEG
    global DNRLEG
    global LARM
    global RARM
    global NECK

    i0 = i0 + UPLLEG_OS
    i1 = i1 + DNLLEG_OS
    i2 = i2 + WAIST_OS
    i3 = i3 + UPRLEG_OS
    i4 = i4 + DNRLEG_OS
    i5 = i5 + LARM_OS
    i6 = i6 + RARM_OS
    i7 = i7 + NECK_OS

    upl_leg = int(NEUTRAL - i0*1.48)
    dnl_leg = int(NEUTRAL - i1*1.48)
    waist = int(NEUTRAL + i2*1.48)
    upr_leg = int(NEUTRAL + i3*1.48)
    dnr_leg = int(NEUTRAL + i4*1.48)
    l_arm = int(NEUTRAL + i5*1.48)
    r_arm = int(NEUTRAL - i6*1.48)
    neck = int(NEUTRAL + i7*1.48)
  
    dif0 = upl_leg - UPLLEG
    dif1 = dnl_leg - DNLLEG
    dif2 = waist - WAIST
    dif3 = upr_leg - UPRLEG 
    dif4 = dnr_leg - DNRLEG
    dif5 = l_arm - LARM
    dif6 = r_arm - RARM
    dif7 = neck - NECK

    for i in range(10):
        tmp0 = UPLLEG + int(dif0 * math.sin(math.radians(i) * 10))
        tmp1 = DNLLEG + int(dif1 * math.sin(math.radians(i) * 10))
        tmp2 = WAIST + int(dif2 * math.sin(math.radians(i) * 10))
        tmp3 = UPRLEG + int(dif3 * math.sin(math.radians(i) * 10))
        tmp4 = DNRLEG + int(dif4 * math.sin(math.radians(i) * 10))
        tmp5 = LARM + int(dif5 * math.sin(math.radians(i) * 10))
        tmp6 = RARM + int(dif6 * math.sin(math.radians(i) * 10))
        tmp7 = NECK + int(dif7 * math.sin(math.radians(i) * 10))

        setPCA9685Duty3(0, 0, tmp0, 0, tmp1, 0, tmp2)
        setPCA9685Duty3(2, 0, tmp2, 0, tmp3, 0, tmp4)
        setPCA9685Duty3(5, 0, tmp5, 0, tmp6, 0, tmp7)
        sleep(0.005)

    UPLLEG = upl_leg
    DNLLEG = dnl_leg
    WAIST = waist
    UPRLEG = upr_leg
    DNRLEG = dnr_leg
    LARM = l_arm
    RARM = r_arm
    NECK = neck
    sleep(DELAY)

def motion2(delay):
    move(0, 0, 0, 0, 0, 0, 0, 0) 
    print("right")      
    move(10, -10, -10, 0,  -10, 18, -18, 0)       
    move(10, -10, -22, 30, -30, 20, -20, 0)       
    move(0,  -20, -15, 40, 15,  25, -25, 0)       
    move(0,  -20,  -5, 25, 10,  20, -20, 0) 
    print("middle")      
    move(0,  -20, 5, 25, 10,  0,   0,  0)   
    print("left")  
    move(0,  -10, 10,10, -10, -18, 18, 0) 
    move(30, -30, 22, 10,-10, -20, 20,0)       
    move(40, 15,  15, 0, -20, -25, 25,0)
    move(25, 10,  5,  0, -20,  -20, 20,0)  
    print("last")     
    move(25, 10,  -5,  0, -20, 0,  0,   0)       
    move(10, -10,  -10,  0, -10, 18, -18, 0) 
    move(0, -10,  0,   0, -10,  0,  0,   0)       
      
def motion(delay):
    move(45, -45, 70,0, 0, 0, 0, 0) 
    #move(0, 0, -70,50, -50, 0, 0, 0) 
 
def stopMove(delay):
    move(0, 0, 0, 0, 0, 0, 0, 0) 

bus = smbus.SMBus(1)
address_pca9685 = 0x40

resetPCA9685()
setPCA9685Freq(50)

NEUTRAL = 276
UPLLEG = 276
DNLLEG = 276
WAIST = 276
UPRLEG = 276
DNRLEG = 276
LARM = 276
RARM = 276
NECK = 276

UPLLEG_OS = 0 
DNLLEG_OS = 0 
WAIST_OS = -15 
UPRLEG_OS = 0 
DNRLEG_OS = 0 
LARM_OS = 0 
RARM_OS = 10 
NECK_OS = 0 

DELAY = 0.5 

try:
    while True:
        motion2(DELAY) 
except KeyboardInterrupt:
    stopMove(DELAY)
    pass
