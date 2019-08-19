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

def setPCA9685Duty8(channel, on1, off1, on2, off2, on3, off3 , on4, off4, on5, off5, on6, off6, on7, off7, on8, off8):
    channelpos = 0x6 + 4*channel
    data = [on1&0xFF, on1>>8, off1&0xFF, off1>>8,
            on2&0xFF, on2>>8, off2&0xFF, off2>>8,
            on3&0xFF, on3>>8, off3&0xFF, off3>>8,
            on4&0xFF, on4>>8, off4&0xFF, off4>>8,
            on5&0xFF, on5>>8, off5&0xFF, off5>>8,
            on6&0xFF, on6>>8, off6&0xFF, off6>>8,
            on7&0xFF, on7>>8, off7&0xFF, off7>>8,
            on8&0xFF, on8>>8, off8&0xFF, off8>>8]
    bus.write_i2c_block_data(address_pca9685, channelpos, data)

def setPCA9685Duty3(channel, on1, off1, on2, off2, on3, off3):
    channelpos = 0x6 + 4*channel
    data = [on1&0xFF, on1>>8, off1&0xFF, off1>>8,
            on2&0xFF, on2>>8, off2&0xFF, off2>>8,
            on3&0xFF, on3>>8, off3&0xFF, off3>>8]
    bus.write_i2c_block_data(address_pca9685, channelpos, data)

def move(i0, i1, i2, i3, i4, i5, i6, i7):
    upl_leg = int(NEUTRAL - i0*1.48)
    dnl_leg = int(NEUTRAL - i1*1.48)
    waist = int(NEUTRAL + i2*1.48)
    upr_leg = int(NEUTRAL + i3*1.48)
    dnr_leg = int(NEUTRAL + i4*1.48)
    l_arm = int(NEUTRAL + i5*1.48)
    r_arm = int(NEUTRAL - i6*1.48)
    neck = int(NEUTRAL + i7*1.48)
    setPCA9685Duty3(0, 0, upl_leg, 0, dnl_leg, 0, waist)
    setPCA9685Duty3(2, 0, waist, 0, upr_leg, 0, dnr_leg)
    setPCA9685Duty3(5, 0, l_arm, 0, r_arm, 0, neck)
    sleep(DELAY)

def motion(delay):
    move(0, 0, 0, 0, 0, 0, 0, 0) 
    move(0,0, 0, 0, 0, 0, 0, -20)       
       
def stopMove(delay):
    setPCA9685Duty8(0, 0, NEUTRAL, 0, NEUTRAL, 0, NEUTRAL, 0, NEUTRAL, 0, NEUTRAL, 0, NEUTRAL, 0, NEUTRAL, 0, NEUTRAL) 
    sleep(delay)

bus = smbus.SMBus(1)
address_pca9685 = 0x40

resetPCA9685()
setPCA9685Freq(50)

NEUTRAL = 276

DELAY = 0.5 

stopMove(DELAY)

try:
    while True:
        motion(DELAY) 
except KeyboardInterrupt:
    stopMove(DELAY)
    pass
