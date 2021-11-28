# General imports
import sys
from os.path import expanduser
import RF24

# NRF configuration

# PIPES (Adresses)
# TX -------- AAA --------> RX
# TX <-------- BBB -------- RX
TX_WRITE_PIPE = b"AAA"
RX_WRITE_PIPE = b"BBB"

SPI_SPEED = 1e6
PA_LEVEL = RF24.RF24_PA_MIN
DATA_RATE = RF24.RF24_250KBPS
CHANNEL = 0x4c
RETRY_DELAY = 3 # between 0 and 15 (0 = 250us and 15 = 15 * 250us = 3.750ms)
RETRY_COUNT = 5 # Between 0 and 15 (with 0 the retry functionality is disabled)

CE_PIN = 25
IRQ_PIN = 0

# Protocol configuration
CHUNKS_SIZE = 1200
SLEEP_DELAY = 0.0001
COMPRESSION_LEVEL = 6


# Frames types
HELLO_TYPE = 0 
CHUNK_INFO_TYPE = 1
DATA_TYPE = 2
CHUNK_IS_GOOD_TYPE = 3

# Others
WORKING_DIR = expanduser("~") + "/working-directory"
