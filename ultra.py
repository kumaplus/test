#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

print ("right")        
print reading(0,17,21)
print ("front")
print reading(0,16,20)
print ("left")
print reading(0,26,27)
