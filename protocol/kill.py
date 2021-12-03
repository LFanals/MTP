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
        if (SW_kill and not has_started):
            os.system("python3 " + utils.MTP_DIR + "main.py &")
            has_started = True
        elif (not SW_kill):
            os.system("bash " + utils.MTP_DIR + "kill.sh")
            # os.system("bash kill.sh")
            has_started = False
            ioparent.reset_leds()
       
        sleep(0.1) 



if __name__ == "__main__":
    main()
