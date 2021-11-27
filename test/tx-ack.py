import RF24
import time

# PIPES (Adresses)
# TX -------- AAA --------> RX
# TX <-------- BBB -------- RX

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


# radio channel 
radio.setChannel(0x4c)

radio.openWritingPipe(b"AAA")
radio.openReadingPipe(1, b"BBB")
radio.powerUp()
radio.printPrettyDetails()

avg = 0
n = 0

radio.stopListening()  # put radio in TX mode

while True:
  n += 1
  a = time.time()
  print(radio.write(b"HolaHolaHolaHola"))
  avg = (avg*(n-1) + (time.time() - a))/n
  print(avg)
  print(radio.read(32))
  # time.sleep(1)




