import RPi.GPIO as GPIO
import time
  
GPIO.setmode(GPIO.BCM)
  
# Declaration of the input pin which is connected with the sensor.
# Additional to that the pull up resistor from the input will be activated.
LED_PIN = 24
GPIO.setup(LED_PIN, GPIO.OUT, initial= GPIO.LOW)
  
print "LED-Test [press ctrl+c to end]"
 
# main program loop
try:
        while True:
                print("LED is on for 4 seconds")
                GPIO.output(LED_PIN,GPIO.HIGH) #LED will be switched on
                time.sleep(4) # Waitmode for 4 seconds
                print("LED is off for 2 Sekunden") 
                GPIO.output(LED_PIN,GPIO.LOW) #LED will be switched off
                time.sleep(2) # Waitmode for another 2 seconds
  
# Scavenging work after the end of the program
except KeyboardInterrupt:
        GPIO.cleanup()
