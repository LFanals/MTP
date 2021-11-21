# PCB map
#                          SW1 - 1: ON, 0: OFF
#                          SW2 - 1: TX, 0: RX
#                          SW3 - 1: NM, 0: MRM|SR
#                          SW4 - 1: MRM, 0: SR
#                          SW5 - X: to determine
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


def config():
    # Config
    GPIO.setmode(GPIO.BOARD) # BOARD selected so I can simply count the pins
    GPIO.setwarnings(False) # Disable GPIO warnings
    
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
    
    GPIO.setup(SW1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SW2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SW3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SW4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SW5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
     
    print("Configured IO")    


def read_switches():
    # Reads inputs two times, with a 100ms delay between, to avoid metastability
    # Returns boolean to indicate if all switches are stable and array with values
    iSW1 = GPIO.input(SW1)
    iSW2 = GPIO.input(SW2)
    iSW3 = GPIO.input(SW3)
    iSW4 = GPIO.input(SW4)
    iSW5 = GPIO.input(SW5)

    time.sleep(0.1)

    iiSW1 = GPIO.input(SW1)
    iiSW2 = GPIO.input(SW2)
    iiSW3 = GPIO.input(SW2)
    iiSW4 = GPIO.input(SW4)
    iiSW5 = GPIO.input(SW5)

    print("Read switches")

    if (iSW1 == iiSW1 and iSW2 == iiSW2 and iSW3 == iiSW3 and iSW4 == iiSW4 and iSW5 == iiSW5):
        return True, [iSW1, iSW2, iSW3, iSW4, iSW5] 
    else:
        return False, [0, 0, 0, 0, 0]


def is_master_on():
    # Returns boolean to indicate SW1 state
    state, SW = read_switches()
    if not(state):
        return False
    else:
        print("Got master switch: ", str(SW[0]))
        if (SW[0] == 1):
            return True
        else:
            return False
            

def control_led(led: int, state: bool):
    # Control led number with a boolean: True = led on
    if (led == 1):
        if (state): GPIO.output(LED1, GPIO.HIGH)
        else: GPIO.output(LED1, GPIO.LOW)
    elif (led == 2):
        if (state): GPIO.output(LED2, GPIO.HIGH)
        else: GPIO.output(LED2, GPIO.LOW)
    elif (led == 3):
        if (state): GPIO.output(LED3, GPIO.HIGH)
        else: GPIO.output(LED3, GPIO.LOW)
    elif (led == 4):
        if (state): GPIO.output(LED4, GPIO.HIGH)
        else: GPIO.output(LED4, GPIO.LOW)
    elif (led == 5):
        if (state): GPIO.output(LED5, GPIO.HIGH)
        else: GPIO.output(LED5, GPIO.LOW)
    else:
        print("Bad led number")

    # print("Controlled led")


def main():
    config() # Configurate switches as inputs and leds as outputs
    while (is_master_on() == False):
        sleep(0.1)  

    state, SW = read_switches() # get switches config, decide which son to run, add logic below
    son.main()


if __name__ == "__main__":
    main()



