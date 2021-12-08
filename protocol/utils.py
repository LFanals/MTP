# General imports
from os.path import expanduser
import configMRM

# NRF configuration

# PIPES (Adresses)
# TX -------- AAA --------> RX
# TX <-------- BBB -------- RX
TX_WRITE_PIPE = b"AAA"
RX_WRITE_PIPE = b"BBB"

CE_PIN = 25
IRQ_PIN = 0

# Frames types
HELLO_TYPE = 0 
CHUNK_INFO_TYPE = 1
DATA_TYPE = 2
CHUNK_IS_GOOD_TYPE = 3

# Others
WORKING_DIR = expanduser("~") + "/working-directory"
MTP_DIR = "/home/pi/MTP/protocol/"
NM_TOP = "/home/pi/MTP_NM/top_level.py"
