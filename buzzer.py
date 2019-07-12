import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
 
#The output pin, which is connected with the buzzer, will be declared here.
GPIO_PIN = 24
GPIO.setup(GPIO_PIN, GPIO.OUT)
#The software-PWM module will be initialized - a frequency of 500Hz will be taken as default.
Frequenz = 500 #In Hertz
pwm = GPIO.PWM(GPIO_PIN, Frequenz)
pwm.start(50)
# The program will wait for the input of a new PWM-frequency from the user.
# Until then, the buzzer will be used with the before inputted frequency (default 500Hz).
try:
    while(True):
        print "----------------------------------------"
        print "Current frequency: %d" % Frequenz
        Frequenz = input("Please input a new frequency (50-5000):")
        pwm.ChangeFrequency(Frequenz)
         
# Scavenging work after the end of the program.
except KeyboardInterrupt:
    GPIO.cleanup()
