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

for i in range(10):
  n += 1
  a = time.time()
  print(radio.write(b"HolaHolaHolaHola"))
  avg = (avg*(n-1) + (time.time() - a))/n
  print(avg)
  radio.startListening()
  timeout = time.monotonic() * 1000 + 200
  while not radio.available() and time.monotonic() * 1000 < timeout:
    pass  # wait for incoming payload or timeout
  radio.stopListening()
  print(radio.read(2))
  # time.sleep(1)

radio.printPrettyDetails()


