import RPi.GPIO as GPIO
from time import sleep
import subprocess

def my_callback(channel):
    if channel==24:
        args = ['sudo', 'poweroff']
        subprocess.Popen(args)

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(24, GPIO.RISING, callback=my_callback, bouncetime=200)

try:
    while True:
        sleep(0.01)

except KeyboardInterrupt:
    pass

GPIO.cleanup()
