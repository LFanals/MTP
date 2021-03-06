import RF24
# Protocol configuration
CHUNKS_SIZE = 100
SLEEP_DELAY = 0.0001
COMPRESSION_LEVEL = 7

SPI_SPEED = int(1e6)
# PA_LEVEL = RF24.RF24_PA_MIN
# PA_LEVEL = RF24.RF24_PA_HIGH
PA_LEVEL = RF24.RF24_PA_MAX
# DATA_RATE = RF24.RF24_1MBPS
DATA_RATE = RF24.RF24_250KBPS
# DATA_RATE = RF24.RF24_2MBPS
# CHANNEL = 0x4c
# CHANNEL = 0x1b
CHANNEL = 27
RETRY_DELAY = 3 # between 0 and 15 (0 = 250us and 15 = 15 * 250us = 3.750ms)
RETRY_COUNT = 5 # Between 0 and 15 (with 0 the retry functionality is disabled)
