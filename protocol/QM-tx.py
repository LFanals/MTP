import argparse
from datetime import datetime
from random import normalvariate
import struct
import sys
import time
import traceback

import pigpio
from nrf24 import *

import os
import glob

#
# A simple NRF24L sender that connects to a PIGPIO instance on a hostname and port, default "localhost" and 8888, and
# starts sending data on the address specified.  Use the companion program "simple-receiver.py" to receive the data
# from it on a different Raspberry Pi.
#
if __name__ == "__main__":    
    os.system("sudo pigpiod")
    print("Python NRF24 Simple Sender Example.")
    
    # Parse command line argument.
    parser = argparse.ArgumentParser(prog="simple-sender.py", description="Simple NRF24 Sender Example.")
    parser.add_argument('-n', '--hostname', type=str, default='localhost', help="Hostname for the Raspberry running the pigpio daemon.")
    parser.add_argument('-p', '--port', type=int, default=8888, help="Port number of the pigpio daemon.")
    parser.add_argument('address', type=str, nargs='?', default='1SNSR', help="Address to send to (3 to 5 ASCII characters).")
    
    args = parser.parse_args()
    hostname = args.hostname
    port = args.port
    address = args.address

    if not (2 < len(address) < 6):
        print(f'Invalid address {address}. Addresses must be 3 to 5 ASCII characters.')
        sys.exit(1)

    # Connect to pigpiod
    print(f'Connecting to GPIO daemon on {hostname}:{port} ...')
    pi = pigpio.pi(hostname, port)
    if not pi.connected:
        print("Not connected to Raspberry Pi ... goodbye.")
        sys.exit()

    # Create NRF24 object.
    # PLEASE NOTE: PA level is set to MIN, because test sender/receivers are often close to each other, and then MIN works better.
    nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.DYNAMIC, channel=27, data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.MIN)
    nrf.set_address_bytes(len(address))
    nrf.open_writing_pipe(address)
    
    # Display the content of NRF24L01 device registers.
    nrf.show_registers()

    os.system("bash /home/pi/MTP/usb/read_usb.sh")

    os.chdir(r'/home/pi/working-directory/')
    myFiles = glob.glob('*.txt')
    filename = myFiles[0]
    print(myFiles)
    
    # filename = "/home/pi/working-directory/a.txt"
    infile = open(filename, 'rb')
    data = infile.read()
    infile.close

    print(len(data))
    print(type(data))
    datae = data + b'\x25\x40\x26'

    i = 0 
    n_success = 0
    n_fail = 0
    try:
        print(f'Send to {address}')
        count = 0
        while i<len(datae):

            n = 31
            payload = struct.pack("<"+"B"*(n+1), 0x01, *datae[i:i+n])
            i += n

            # vec = struct.pack("<"+"B"*n, *datae[i:i+n])
            # print(vec)
            # payload = struct.pack("<BB", 0x01, temperature)

            # Send the payload to the address specified above.
            nrf.reset_packages_lost()
            nrf.send(payload)
            try:
                nrf.wait_until_sent()
            except TimeoutError:
                print('Timeout waiting for transmission to complete.')
                # Wait 10 seconds before sending the next reading.
                time.sleep(0.01)
                continue
            
            if nrf.get_packages_lost() == 0:
                # print(f"Success: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")
                n_success += 1
            else:
                # print(f"Error: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")
                n_fail += 1
                print("total success: ", str(n_success), ", total fail: ", str(n_fail))

            # Wait 10 seconds before sending the next reading.
            # time.sleep(0.01)
    except:
        traceback.print_exc()
        nrf.power_down()
        pi.stop()





