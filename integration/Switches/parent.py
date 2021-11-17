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

import son

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
# iSWx and iiSWx act as two chained registers. rSWx changes state if iSWx==iiSWx
rSW1, iSW1, iiSW1 = 0, 0, 0
rSW2, iSW2, iiSW2 = 0, 0, 0
rSW3, iSW3, iiSW3 = 0, 0, 0
rSW4, iSW4, iiSW4 = 0, 0, 0
rSW5, iSW5, iiSW5 = 0, 0, 0


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
     
    print("Configured IO")    


def read_switches():
    iSW1 = GPIO.input(SW1)
    iSW2 = GPIO.input(SW2)
    iSW3 = GPIO.input(SW2)
    iSW4 = GPIO.input(SW4)
    iSW5 = GPIO.input(SW5)

    iiSW1 = iSW1
    iiSW2 = iSW2
    iiSW3 = iSW3
    iiSW4 = iSW4
    iiSW5 = iSW5

    if (iSW1 == iiSW1): rSW1 = iSW1
    if (iSW2 == iiSW2): rSW2 = iSW2
    if (iSW3 == iiSW3): rSW3 = iSW3
    if (iSW4 == iiSW4): rSW4 = iSW4
    if (iSW5 == iiSW5): rSW5 = iSW5
 
    print("Read switches")


def read_master_sw():

    read_switches()
    print("Got master switch: ", str(rSW1))

    if (rSW1 == 1): 
        return True
    elif (rSW1 == 0): 
        return False


def control_led(led: int, state: bool):
    if (led == 1):
        if (bool): GPIO.output(LED1, GPIO.HIGH)
        else: GPIO.output(LED1, GPIO.LOW)
    elif (led == 2):
        if (bool): GPIO.output(LED2, GPIO.HIGH)
        else: GPIO.output(LED2, GPIO.LOW)
    elif (led == 3):
        if (bool): GPIO.output(LED3, GPIO.HIGH)
        else: GPIO.output(LED3, GPIO.LOW)
    elif (led == 4):
        if (bool): GPIO.output(LED4, GPIO.HIGH)
        else: GPIO.output(LED4, GPIO.LOW)
    elif (led == 5):
        if (bool): GPIO.output(LED5, GPIO.HIGH)
        else: GPIO.output(LED1, GPIO.LOW)
    else:
        print("Bad led number")

    print("Controlled led")


def main():
    config()
    while (read_master_sw() == False):
        sleep(0.1)  

    read_switches() # get switches config, decide which son to run
    son.main()


if __name__ == "__main__":
    main()



