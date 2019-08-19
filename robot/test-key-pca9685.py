# -*- coding: utf-8 -*-
from time import sleep
import smbus
import math
import readchar

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

def move(l0, l2, r4, r6):
    setPCA9685Duty(0, 0, l0)
    setPCA9685Duty(2, 0, l2)
    setPCA9685Duty(4, 0, r4)
    setPCA9685Duty(6, 0, r6)
    
    sleep(0.1)

def move_ini():
    setPCA9685Duty(0, 0, 276)
    setPCA9685Duty(2, 0, 276)
    setPCA9685Duty(4, 0, 276)
    setPCA9685Duty(6, 0, 276)
    
    sleep(1) 

def move_forward():
    move(276, 209, 276, 209)
    move(276, 179, 276, 179)  
    move(313, 276, 313, 276) 
    move(343, 276, 343, 276)
    move(276, 313, 276, 313)
    move(276, 343, 276, 343)
    move(209, 276, 209, 276)
    move(179, 276, 179, 276) 

def move_backward():
    move(276, 209, 276, 209)
    move(276, 179, 276, 179)
    move(209, 276, 209, 276) 
    move(179, 276, 179, 276)
    move(276, 313, 276, 313)
    move(276, 343, 276, 343)
    move(313, 276, 313, 276)
    move(343, 276, 343, 276) 

def move_left():
    move(276, 209, 276, 209)
    move(276, 179, 276, 179)
    move(343, 276, 276, 276) 
    move(373, 276, 306, 276) 
    move(276, 313, 276, 313)
    move(276, 343, 276, 343)
    move(276, 276, 343, 276)
    move(306, 276, 373, 276) 

def move_right():
    move(276, 209, 276, 209)
    move(276, 179, 276, 179)
    move(209, 276, 276, 276) 
    move(179, 276, 246, 276) 
    move(276, 313, 276, 313)
    move(276, 343, 276, 343)
    move(276, 276, 209, 276)
    move(246, 276, 179, 276) 

bus = smbus.SMBus(1)
address_pca9685 = 0x40

resetPCA9685()
setPCA9685Freq(50)

move_ini()

dict = 0

try:
    while True:
        val2 = readchar.readchar
        val = readchar.readkey()
        print(val)

        if val == "F":
            dict = 2
        elif val == "B":
            dict = 1
        elif val == "R":
            dict = 3
        elif val == "L":
            dict = 4
        else:
            dict = 5

        print(dict)

        if dict == 1:
            move_backward()
        elif dict == 2:
            move_forward()
        elif dict == 3:
            move_right()
        elif dict == 4:
            move_left()
        else:
            print("ini") 
            move_ini()

except KeyboardInterrupt:
    pass

