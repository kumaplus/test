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

def move():
    setPCA9685Duty(0, 0, 209)
    setPCA9685Duty(1, 0, 343)
    sleep(0.2)
    setPCA9685Duty(0, 0, 343)
    setPCA9685Duty(1, 0, 209)
    sleep(0.2)

bus = smbus.SMBus(1)
address_pca9685 = 0x40

resetPCA9685()
setPCA9685Freq(50)

for i in range(16):
    setPCA9685Duty(i, 0, 276)

try:
    while True:
        move()

except KeyboardInterrupt:
    pass
