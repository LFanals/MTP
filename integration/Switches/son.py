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

import parent


def main():
    while True:
        print("son loop") 
        parent.control_led(2, True)

        if (read_master_sw() = False): # Master switch goes to 0
            print("Son execution finished")

        sleep(0.1)  


if __name__ == "__main__":
    main()



