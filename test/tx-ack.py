import RF24
import time

# PIPES (Adresses)
# TX -------- TXRX --------> RX
# TX <-------- RXTX -------- RX

radio = RF24.RF24(1000000)
# radio = RF24.RF24(10000000)
radio.begin(25, 0) #Set CE and IRQ pins
radio.setDataRate(RF24.RF24_250KBPS)
# radio.setDataRate(RF24.RF24_2MBPS)

radio.setRetries(3,5)


# radio.setPALevel(RF24.RF24_PA_MAX)
radio.setPALevel(RF24.RF24_PA_MIN)

# ACK payloads are dynamically sized.
radio.enableDynamicPayloads()  # to use ACK payloads

# to enable the custom ACK payload feature
radio.enableAckPayload()



radio.openWritingPipe(b"TXRX")
radio.openReadingPipe(1, b"RXTX")
radio.powerUp()
radio.printDetails()

avg = 0
n = 0
while True:
  n += 1
  a = time.time()
  print(radio.write(b"HolaHolaHolaHola"))
  avg = (avg*(n-1) + (time.time() - a))/n
  print(avg)
  # time.sleep(1)




