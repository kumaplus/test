import RPi.GPIO as GPIO
import time
   
GPIO.setmode(GPIO.BCM)
   
# The input pin of the sensor will be declared. Additional to that the pull up resistor will be activated
GPIO_PIN = 24
GPIO.setup(GPIO_PIN, GPIO.IN)
   
print "Sensor-Test [press ctrl+c to end]"
   
# This output function will be started at signal detection
def outFunction(null):
        print("Signal detected")
   
# At the moment of detection a signal (falling signal edge) the output function will be activated.
GPIO.add_event_detect(GPIO_PIN, GPIO.FALLING, callback=outFunction, bouncetime=100) 
   
# main program loop
try:
        while True:
                time.sleep(1)
   
# Scavenging work after the end of the program
except KeyboardInterrupt:
        GPIO.cleanup()
