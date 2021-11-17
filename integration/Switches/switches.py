# PCB map
#                          SW1 - 1: ON, 0: OFF
#                          SW2 - 1: TX, 0: RX
#                          SW3 - may not be available to give space to the SD card
#                          SW4 - 1: NM, 0: MRM|SR
#                          SW5 - 1: MRM, 0: SR
# LED1 LED2 LED3 LED4 LED5

import RPi.GPIO as GPIO                           
import time
from time import sleep

# LED outputs, initialized at low level
LED1 = 18
LED2 = 16
LED3 = 12
LED4 = 10
LED5 = 8

# Switches pull down inputs (i.e., there's a 50k ohm resitance between the pin and ground. 
# To have a 1 3.3V must be connected to the pin, if the switch is open a 0 is expected.
SW1 = 15
SW2 = 13
SW3 = 11
SW4 = 7
SW5 = 5

# Initialize states
iSW1, iiSW1 = 0, 0
iSW2, iiSW2 = 0, 0
iSW3, iiSW3 = 0, 0
iSW4, iiSW4 = 0, 0
iSW5, iiSW5 = 0, 0



def config():
     # Config
     GPIO.setmode(GPIO.BOARD)                              #BOARD selected so I can simply count the pins
     GPIO.setwarnings(False)                               #Disable GPIO warnings
     
     # Outputs
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
     
     # Inputs     
     GPIO.setup(SW1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
     GPIO.setup(SW2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
     GPIO.setup(SW3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
     GPIO.setup(SW4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
     GPIO.setup(SW5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
     

def main():
    config()
    while True:
        iSW1 = GPIO.input(SW1)
        iSW2 = GPIO.input(SW2)
        iSW3 = GPIO.input(SW2)
        iSW4 = GPIO.input(SW4)
        iSW5 = GPIO.input(SW5)
    
        sleep(0.1)  


if __name__ == "__main__":
    main()
