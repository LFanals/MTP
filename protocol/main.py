import sys
from mtp_receiver import start_receiver
from mtp_sender import start_sender
import ioparent
from time import sleep
import os

def main():
    
    os.system("sudo pigpiod")
    # Get transmitter or receiver arguments
    ioparent.config()
    ioparent.control_led(1, False)
    ioparent.control_led(2, False)
    ioparent.control_led(3, False)
    ioparent.control_led(4, False)
    ioparent.control_led(5, False)

    while (ioparent.is_master_on() == False):
        sleep(0.1)  

    state, SW = ioparent.read_switches() # get switches config, decide which son to run, add logic below
    print("Master switch set to 1. Reading configuration")
    ioparent.control_led(1, True)

    if SW[2] == 1: 
        print("SW[2] == 1 --> Mode: NM")
        #TODO: link with NM logic
    else:
        print("SW[2] == 0 --> Mode: MRM or SR")
        if SW[3] == 1:
            print("SW[3] == 1 --> Mode: MRM")
        else:
            print("SW[3] == 0 --> Mode: SR")

        if SW[1] == 1:
            print("SW[1] == 1 --> Starting communcation as: SENDER")
            start_sender()
        else:
            print("SW[1] == 0 --> Starting communcation as: RECEIVER")
            start_receiver()

if __name__ == "__main__":
    main()
