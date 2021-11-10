import chunk_creator
import packet_creator

import argparse
from datetime import datetime
from random import normalvariate
import struct
import sys
import time
import traceback

import pigpio
from nrf24 import *

HELLO_PREFIX = 0
CHUNK_INFO_PREFIX = 1
DATA_PREFIX = b'\x02'
SUBCHUNK_SIZE = 31
PAYLOAD_SIZE = 32

def main():
    chunk_size = 100

    # Creating Chunks
    chunk_list = chunk_creator.get_file_chunks("large_entire.txt", chunk_size)
    chunk_amount = len(chunk_list)
    print("Number of compressed chunks: " + str(chunk_amount))
    
    # Creating hello frame
    hello_frame = packet_creator.create_hello_frame(chunk_amount)
    print("    " + packet_creator.dump(hello_frame))
    print("    length: " + str(len(hello_frame)))

    # Creating chunk_info frame
    chunk_info_frame = packet_creator.create_chunk_info_frame(106, 3)
    print("    " + packet_creator.dump(chunk_info_frame))
    print("    length: " + str(len(chunk_info_frame)))
    
    # Creating data frames
    rts_chunk_list = packet_creator.create_data_frames(chunk_list)
    print("Number of chunks: " + str(len(rts_chunk_list)))
    subchunk_amount = len(rts_chunk_list[3])
    print("Number of subchunks per chunk: " + str(len(rts_chunk_list[3])))
    print("    " + packet_creator.dump(rts_chunk_list[3][2]))


    ############################################################################
    ###########################  Test Communication  ###########################
    ############################################################################

    # Starting TEST simple sender
    print("Python NRF24 Simple Sender Example.")
    
    # Parse command line argument.
    parser = argparse.ArgumentParser(prog="main.py", description="Simple NRF24 Sender Example.")
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
    nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.DYNAMIC, channel=100, data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.LOW)
    nrf.set_address_bytes(len(address))
    nrf.open_writing_pipe(address)
    
    # Display the content of NRF24L01 device registers.
    nrf.show_registers()

    try:
        print(f'Send to {address}')
        i = 0
        payload = hello_frame
        while i < subchunk_amount + 2:

            if (i == 0): 
                payload = hello_frame
                print("Sending hello_frame")
            elif (i == 1): 
                payload = chunk_info_frame
                print("Sending chunk_info_frame")
            else: 
                payload = rts_chunk_list[0][i-2]
                print("Sending data_frame")

            # Send the payload to the address specified above.
            nrf.reset_packages_lost()
            nrf.send(payload)
            try:
                nrf.wait_until_sent()
            except TimeoutError:
                print('Timeout waiting for transmission to complete.')
                # Wait 10 seconds before sending the next reading.
                time.sleep(10)
                continue
            
            if nrf.get_packages_lost() == 0:
                print(f"Success: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")
            else:
                print(f"Error: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")

            i += 1
            time.sleep(0.1)
        
    except:
        traceback.print_exc()
        nrf.power_down()
        pi.stop()

if __name__ == "__main__":
    main()

