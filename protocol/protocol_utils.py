# General imports
import pigpio
import sys
from os.path import expanduser

# NRF24 Address
ADDRESS = "MTPC"

# Working directory path
WORKING_DIR = expanduser("~") + "/working-directory"

# Prefixes for packets
HELLO_PREFIX = 0
CHUNK_INFO_PREFIX = 1
DATA_PREFIX = 2
CHUNK_IS_GOOD_PREFIX = 3

def connect_to_gpio(hostname, port):
    # Connect to pigpiod
    print(f'Connecting to GPIO daemon on {hostname}:{port} ...')
    pi = pigpio.pi(hostname, port)
    if not pi.connected:
        print("Not connected to Raspberry Pi ... goodbye.")
        sys.exit()
    return pi