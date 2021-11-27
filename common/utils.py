# General imports
import pigpio
import sys
from os.path import expanduser
import RF24

# NRF configuration
PIPE = bytearray([ 0x52, 0x78, 0x41, 0x41, 0x41 ])
SPI_SPEED = 1e6
PA_LEVEL = RF24.RF24_PA_MIN
DATA_RATE = RF24.RF24_250KBPS
CHANNEL = 0x4c

CE_PIN = 25
IRQ_PIN = 0

# Protocol configuration
CHUNKS_SIZE = 1200

# Others
WORKING_DIR = expanduser("~") + "/working-directory"

def connect_to_gpio(hostname, port):
    # Connect to pigpiod
    print(f'Connecting to GPIO daemon on {hostname}:{port} ...')
    pi = pigpio.pi(hostname, port)
    if not pi.connected:
        print("Not connected to Raspberry Pi ... goodbye.")
        sys.exit()
    return pi