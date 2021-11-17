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


def main():
    while True:
        print("son loop") 
        sleep(0.1)  


if __name__ == "__main__":
    main()



