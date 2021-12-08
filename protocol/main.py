from receiver import start_receiver
from sender import start_sender, working_directory_contains_file
import ioparent
from time import sleep
import os
import subprocess

import utils

def main():
    # Get transmitter or receiver arguments
    ioparent.config()

    status = 1
    led_active = True
    ioparent.reset_leds()
    ioparent.control_led(1, True)
    while status != 0:
        SW = ioparent.read_switches()
        is_TX = SW[ioparent.TX_RX_SWITCH]
        is_NM = SW[ioparent.NM_MODE_SWITCH]

        while ioparent.is_master_on():
            sleep(0.5)  
            ioparent.control_led(3, led_active)
            led_active = not led_active
        ioparent.control_led(3, False)

        is_usb_read = False 
        while not ioparent.is_master_on():
            SW = ioparent.read_switches()
            is_TX = SW[ioparent.TX_RX_SWITCH]
            if not is_usb_read and is_TX:
                os.system("bash " + utils.MTP_DIR + "read_usb.sh")
                if working_directory_contains_file():   
                    is_usb_read = True
                    ioparent.control_led(5, True)
            sleep(0.1)  

        ioparent.reset_leds()
        ioparent.control_led(1, False)
        ioparent.control_led(2, True)
        ioparent.control_led(5, False)
        
        SW = ioparent.read_switches()
        is_NM = SW[ioparent.NM_MODE_SWITCH]

        if is_NM: 
            print("SW[3] == 1 --> Mode: NM")
            #TODO: link with NM logic
            os.system("python3 " + utils.NM_TOP)
        else:
            print("SW[3] == 0 --> Mode: MRM or SR")

            if is_TX:
                while not working_directory_contains_file():
                    os.system("bash " + utils.MTP_DIR + "read_usb.sh")
        
                print("SW[1] == 1 --> Starting communcation as: SENDER")
                status = start_sender()
                ioparent.reset_leds()
            else:
                print("SW[1] == 0 --> Starting communcation as: RECEIVER")
                os.system("bash " + utils.MTP_DIR + "clear_working_dir.sh")
                status = start_receiver()
                ioparent.reset_leds()
                ioparent.control_led(1, True)
                os.system("bash " + utils.MTP_DIR + "write_usb.sh")
        
            if status: 
                print("\nMANUAL INTERRUPT")
                ioparent.control_led(5, True)
                ioparent.control_led(2, True)
            else: 
                print("\nFINISHED CORRECTLY")
                ioparent.control_led(1, True)
                ioparent.control_led(2, True)
                

        sleep(0.1) 
        
    

if __name__ == "__main__":
    main()
