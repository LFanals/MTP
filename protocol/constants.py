from nrf24 import *

CHANNEL = 100
DATA_RATE = RF24_DATA_RATE.RATE_250KBPS
PA_LEVEL = RF24_PA.LOW
RETRY_DELAY = 0.0001
CHUNK_SIZE = 20
PAYLOAD_SIZE = RF24_PAYLOAD.ACK
SPI_SPEED = 1e6
COMPRESSION_LEVEL = 9