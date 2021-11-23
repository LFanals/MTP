# General imports
import pigpio
import sys
from os.path import expanduser

ADDRESS = "MTPC"
WORKING_DIR = expanduser("~") + "/working-directory"

def connect_to_gpio(hostname, port):
    # Connect to pigpiod
    print(f'Connecting to GPIO daemon on {hostname}:{port} ...')
    pi = pigpio.pi(hostname, port)
    if not pi.connected:
        print("Not connected to Raspberry Pi ... goodbye.")
        sys.exit()
    return pi