# -*- coding: utf-8 -*-
from time import sleep
import smbus
import math
from evdev import InputDevice, categorize, ecodes, KeyEvent

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
    
    sleep(0.2)

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

gamepad = InputDevice('/dev/input/event0')

dict = 0

move_forward()

try:
    for event in gamepad.read_loop():
        if event.type == ecodes.EV_KEY:
            keyevent = categorize(event)
            if keyevent.keystate == KeyEvent.key_down:
                if keyevent.keycode[0] == 'BTN_A':
                    print("Back")
                    dict = 1 
                elif keyevent.keycode[0] == 'BTN_WEST':
                    print("Forward")
                    dict = 2
                elif keyevent.keycode[0] == 'BTN_B':
                    print("Right")
                    dict = 3
                elif keyevent.keycode[0] == 'BTN_NORTH':
                    print("Left")
                    dict = 4 
                elif keyevent.keycode == 'BTN_THUMBR' or keyevent.keycode == 'BTN_THUMBL':
                    print("Stop")
                    dict = 0
                elif keyevent.keycode == 'BTN_TR':
                    print("Faster")
                elif keyevent.keycode == 'BTN_TL':
                    print("Slower")
                elif keyevent.keycode == 'BTN_SELECT':
                    print("Up")
                elif keyevent.keycode == 'BTN_START':
                    print("Down")
        if event.type == ecodes.EV_ABS:
            keyevent = categorize(event)
            if keyevent.event.code == 16:
                print(reading(0))

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
            #move_ini()

except KeyboardInterrupt:
    pass

