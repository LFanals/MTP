import sys
from receiver import start_receiver
from sender import start_sender
import ioparent
from time import sleep
import os

import utils

def main():
    # os.system("sudo killall pigpiod")
    # os.system("sudo pigpiod")
    # Get transmitter or receiver arguments
    ioparent.config()

    status = 1
    ioparent.reset_leds()
    ioparent.control_led(1, True)
    while status != 0:
        # os.system("sudo killall pigpiod")
        while not ioparent.is_master_on():
            sleep(0.1)  

        ioparent.reset_leds()
        ioparent.control_led(1, False)
        ioparent.control_led(2, True)
        SW = ioparent.read_switches() # get switches config, decide which son to run, add logic below
        print("Master switch set to 1. Reading configuration")
        is_TX = SW[1]
        is_NM = SW[2]
        mode = SW[3]

        if is_NM: 
            print("SW[2] == 1 --> Mode: NM")
            #TODO: link with NM logic
        else:
            print("SW[2] == 0 --> Mode: MRM or SR")
            if mode: print("SW[3] == 1 --> Mode: MRM")
            else: print("SW[3] == 0 --> Mode: SR")

            if is_TX:
                print("SW[1] == 1 --> Starting communcation as: SENDER")
                status = start_sender(mode)
            else:
                print("SW[1] == 0 --> Starting communcation as: RECEIVER")
                os.system("bash " + utils.MTP_DIR + "clear_working_dir.sh")
                status = start_receiver(mode)
                os.system("bash " + utils.MTP_DIR + "write_usb.sh")
        
            if status: 
                print("\nMANUAL INTERRUPT")
                ioparent.reset_leds()
                ioparent.control_led(5, True)
                ioparent.control_led(2, True)
            else: 
                print("\nFINISHED CORRECTLY")
                ioparent.reset_leds()
                ioparent.control_led(1, True)
                ioparent.control_led(2, True)
                

        sleep(0.1) 
        
    

if __name__ == "__main__":
    main()
