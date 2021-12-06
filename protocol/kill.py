import ioparent
from time import sleep
import os
import utils


def main():

    has_started = False
    ioparent.config()
    while True:

        SW = ioparent.read_switches() # get switches config, decide which son to run, add logic below
        SW_kill = SW[ioparent.KILL_SWITCH]
        SW_master = SW[ioparent.MASTER_SWITCH]
        SW_network = SW[ioparent.NM_MODE_SWITCH]
        SW_tx = SW[ioparent.TX_RX_SWITCH]

        if SW_kill and not has_started:
            os.system("python3 " + utils.MTP_DIR + "main.py &")
            has_started = True
        elif not SW_kill:
            os.system("bash " + utils.MTP_DIR + "kill.sh")
            has_started = False
            ioparent.reset_leds()

        elif not SW_master and not SW_network and not SW_tx and has_started:
            # We stop the receiver and wait until we are able to write to usb
            ioparent.reset_leds()
            has_started = False
            os.system("bash " + utils.MTP_DIR + "kill.sh")
            ioparent.control_led(1, True)
            os.system("bash " + utils.MTP_DIR + "write_usb.sh")
            ioparent.control_led(2, True)
       
        sleep(0.1) 



if __name__ == "__main__":
    main()
