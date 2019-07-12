# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
from evdev import InputDevice, categorize, ecodes, KeyEvent
import subprocess

def move_car(dir):
    if dir == 0:
        #foward
        move_ChangeDutyCycle(speed, 0, speed, 0)
    elif dir == 1:
        #back 
        move_ChangeDutyCycle(0, speed, 0, speed)
    elif dir == 2:
        #right
        move_ChangeDutyCycle(0, speed, speed, 0)
    elif dir == 3:
        #left
        move_ChangeDutyCycle(speed, 0, 0, speed)
    else:
        #stop
        move_ChangeDutyCycle(0, 0, 0, 0)

def move_ChangeDutyCycle(val, val1, val2, val3):
    p0.ChangeDutyCycle(val)
    p1.ChangeDutyCycle(val1)
    p2.ChangeDutyCycle(val2)
    p3.ChangeDutyCycle(val3) 

def auto_move():
    #front
    res_f = reading(0,16,20)
    res_r = reading(0,17,21)
    res_l = reading(0,26,27)
    print("forward : " + str(res_f))
    print("right   : " + str(res_r))
    print("left    : " + str(res_l))
    if res_f < 20:
        if res_r > res_l:
            move_car(2)
            print("right")
        else:
            move_car(3)
            print("left")
    else:
        if res_r < 20:
            move_car(3)
            print("left")
        elif res_l < 20:
            move_car(2)
            print("right")
        else: 
            move_car(0)

def print_out(str):
    if True:
        print(str)

def reading(sensor,trig,echo):
    if sensor == 0:
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
        print("Incorrect usonic() function varible.") 

GPIO.setmode(GPIO.BCM)

GPIO.setup(25, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.add_event_detect(21, GPIO.RISING, callback=my_callback, bouncetime=200)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(20,GPIO.IN)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(21,GPIO.IN)
GPIO.setup(26,GPIO.OUT)
GPIO.setup(27,GPIO.IN)
p0 = GPIO.PWM(25, 50)
p1 = GPIO.PWM(24, 50)
p2 = GPIO.PWM(23, 50)
p3 = GPIO.PWM(22, 50)
p = GPIO.PWM(18, 50)
p4 = GPIO.PWM(4, 50)
p5 = GPIO.PWM(5, 50)
p6 = GPIO.PWM(6, 50)
p.start(6.75)

p0.start(0)
p1.start(0)
p2.start(0)
p3.start(0)
p4.start(0)
p5.start(0)
p6.start(0)

speed = 70
gamepad = InputDevice('/dev/input/event0')
val = 2000 

move_car(0)

try:
    while 1:
        auto_move()
except KeyboardInterrupt:
    print("except")
    GPIO.cleanup()
