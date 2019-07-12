import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(25, GPIO.LOW)

try:
    while True:
        if GPIO.input(24) == True:
            GPIO.output(25, GPIO.LOW)
            print "No obstacle"
        else:
            GPIO.output(25, GPIO.HIGH)
            print "Obstacle detected"

        sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()

