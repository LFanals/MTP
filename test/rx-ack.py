import RF24
import time

import struct

pipes = [ 0x52, 0x78, 0x41, 0x41, 0x41 ] 
pipesbytes = bytearray(pipes)

# PIPES
# TX -------- AAA --------> RX
# TX <-------- BBB -------- RX

radio = RF24.RF24(1000000)
# radio = RF24.RF24(10000000)
radio.begin(25, 0) #Set CE and IRQ pins
radio.setPALevel(RF24.RF24_PA_MIN)
radio.setDataRate(RF24.RF24_250KBPS)
radio.setRetries(3,5)

# ACK payloads are dynamically sized.
radio.enableDynamicPayloads()  # to use ACK payloads

# to enable the custom ACK payload feature
radio.enableAckPayload()

radio.setChannel(0x4c)
radio.openWritingPipe(b"BBB")
radio.openReadingPipe(1, b"AAA")
radio.powerUp()
radio.printPrettyDetails()

#radio.powerUp()
cont=0

radio.startListening()  # put radio in RX mode

while True:
  #pipe = [1]

  #radio.writeAckPayload(1, b"xd")  # load ACK

  while not radio.available():
    # time.sleep(0.250)
    time.sleep(0.000001)
    

  recv_buffer = bytearray([])
  recv_buffer = radio.read(16)
  radio.stopListening()
  print(recv_buffer)
  print(radio.write(b"xd"))
  radio.startListening()
