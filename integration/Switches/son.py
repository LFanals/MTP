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

import parent


def main():
    print("Son loop") 
    parent.config()
    while True:
            
        if (parent.is_master_on() == True): # Master switch goes to 0, the son programs have to stop
            print("Son execution started")

        parent.control_led(1, True)
        parent.control_led(2, True)
        parent.control_led(3, True)
        parent.control_led(4, True)
        parent.control_led(5, True)
        sleep(0.5)
        parent.control_led(1, False)
        parent.control_led(2, False)
        parent.control_led(3, False)
        parent.control_led(4, False)
        parent.control_led(5, False)
        sleep(0.5)

        if (parent.is_master_on() == False): # Master switch goes to 0, the son programs have to stop
            print("Son execution finished")


if __name__ == "__main__":
    main()



