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
    elif dir ==3:
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

def auto_stop():
    res = reading(0)
    print(res)
    if res < 20:
        print("auto stop")
        move_car(4)

def servo_duty_hwpwm():
    val_min = 0
    val_max = 4095
    # デューティ比0%を0、100%を1024として数値を入力
    servo_min = 3.5   # 50Hz(周期20ms)、デューティ比3.5%: 3.5*1024/100=約36
    servo_max = 10.0  # 50Hz(周期20ms)、デューティ比10%: 10*1024/100=約102
    duty = int((servo_min-servo_max)*(val-val_min)/(val_max-val_min) + servo_max)
    # 一般的なサーボモーターはこちらを有効に
    #duty = int((servo_max-servo_min)*(val-val_min)/(val_max-val_min) + servo_min)
    p.ChangeDutyCycle(duty) 

def led_on(col):
    if col == 0:
        #blue
        led_ChangeDutyCycle(100, 0, 0)
    elif col == 1:
        #green
        led_ChangeDutyCycle(0, 100, 0)
    elif col == 2:
        #red
        led_ChangeDutyCycle(0, 0, 100)
    elif col == 3:
        #yellow
        led_ChangeDutyCycle(0, 100, 100)
    else:
        led_ChangeDutyCycle(0, 0, 0)

def led_ChangeDutyCycle(val, val1, val2):
    p4.ChangeDutyCycle(val)
    p5.ChangeDutyCycle(val1)
    p6.ChangeDutyCycle(val2)

def my_callback(channel):
    print("")
    #print("poweroff")
    #print(channel)
    #if channel==21:
    #    args = ['sudo', 'poweroff']
    #    subprocess.Popen(args)

def print_out(str):
    if True:
        print(str)

def reading(sensor):
    if sensor == 0:
        GPIO.output(TRIG, GPIO.LOW)
        time.sleep(0.3)

        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO) == 0:
            signaloff = time.time()

        while GPIO.input(ECHO) == 1:
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
TRIG = 16
ECHO = 20
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
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

speed = 60
gamepad = InputDevice('/dev/input/event0')
val = 2000 

led_on(4)

print(reading(0))

flg_dir = 1
cnt = 0

try:
    for event in gamepad.read_loop():
        if cnt == 5: 
            auto_stop()
            cnt=0 
        else:
            cnt+=1

        if event.type == ecodes.EV_KEY:
            keyevent = categorize(event)
            if keyevent.keystate == KeyEvent.key_down:
                if keyevent.keycode[0] == 'BTN_A':
                    print_out("Back")
                    move_car(1)
                    led_on(0)
                elif keyevent.keycode[0] == 'BTN_WEST':
                    print_out("Forward")
                    move_car(0)
                    led_on(1)
                elif keyevent.keycode[0] == 'BTN_B':
                    print_out("Right")
                    move_car(2)
                    led_on(2)  
                elif keyevent.keycode[0] == 'BTN_NORTH':
                    print_out("Left")
                    move_car(3)
                    led_on(3)
                elif keyevent.keycode == 'BTN_THUMBR' or keyevent.keycode == 'BTN_THUMBL':
                    print_out("Stop")
                    move_car(4)
                    led_on(4) 
                elif keyevent.keycode == 'BTN_TR':
                    print_out("Faster")
                    speed += 5 
                    if speed > 100:
                        speed = 100 
                elif keyevent.keycode == 'BTN_TL':
                    print_out("Slower")
                    speed -= 5
                    if speed < 0:
                        speed = 0
                elif keyevent.keycode == 'BTN_SELECT':
                    print_out("Up")
                    val += 200 
                    if val > 4095:
                        val = 4095
                    servo_duty_hwpwm()
                elif keyevent.keycode == 'BTN_START':
                    print_out("Down")
                    val -= 200 
                    if val < 0:
                        val = 0
                    servo_duty_hwpwm()
        if event.type == ecodes.EV_ABS:
            keyevent = categorize(event)
            if keyevent.event.code == 16:
                print(reading(0))
       
except KeyboardInterrupt:
    pass
finally:
    p0.stop()
    p1.stop()
    p2.stop()
    p3.stop()
    p4.stop()
    p5.stop()
    p6.stop()
    p.stop()
    GPIO.cleanup()
