import ioparent
from time import sleep
import os


def main():

    has_started = False
    ioparent.config()
    while True:

        SW = ioparent.read_switches() # get switches config, decide which son to run, add logic below
        SW_kill = SW[ioparent.KILL_SWITCH]
        if (SW_kill and not has_started):
            os.system("python3 main.py &")
            has_started = True
        elif (not SW_kill):
            os.system("sudo bash kill.sh")
            has_started = False
            ioparent.reset_leds()
       
        sleep(0.1) 



if __name__ == "__main__":
    main()
