import RPi.GPIO as GPIO                           
import time
from time import sleep

# Config
GPIO.setmode(GPIO.BOARD)                              #BOARD selected so I can simply count the pins
GPIO.setwarnings(False)                               #Disable GPIO warnings

# LED outputs, initialized at low level
LED1 = 18
LED2 = 16
LED3 = 12
LED4 = 10
LED5 = 8

GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
GPIO.setup(LED3, GPIO.OUT)
GPIO.setup(LED4, GPIO.OUT)
GPIO.setup(LED5, GPIO.OUT)

GPIO.output(LED1, GPIO.LOW)
GPIO.output(LED2, GPIO.LOW)
GPIO.output(LED3, GPIO.LOW)
GPIO.output(LED4, GPIO.LOW)
GPIO.output(LED5, GPIO.LOW)

# Switches pull down inputs (i.e., there's a 50k ohm resitance between the pin and ground. 
# To have a 1 3.3V must be connected to the pin, if the switch is open a 0 is expected.
SW1 = 15
SW2 = 13
SW3 = 11
SW4 = 7
SW5 = 5

GPIO.setup(SW1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Initialize states
iSW1 = 0
iSW2 = 0
iSW3 = 0
iSW4 = 0
iSW5 = 0


# Loop
while True:
    iSW1 = GPIO.input(SW1)
    iSW2 = GPIO.input(SW2)
    iSW3 = GPIO.input(SW2)
    iSW4 = GPIO.input(SW4)
    iSW5 = GPIO.input(SW5)

    print(iSW1)
    
    sleep(0.5)  
