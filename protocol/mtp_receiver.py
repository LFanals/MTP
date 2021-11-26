# local imports 
import protocol_utils as p_utils
import chunk_handler
#import ioparent

# nrf24 library import
from nrf24 import *
import constants

# general imports
import time
from datetime import datetime
import sys
import os
import subprocess

def start_receiver():
    print("Starting receiver")

    # Setup nrf24
    nrf = setup_receiver()

    # Clean working directory
    filename = os.path.join(p_utils.WORKING_DIR, "received.txt")
    print("File to be received: " + filename)
    clean_working_dir(filename)

    # Wait for Hello frame until we receive it
    is_hello = False
    while not is_hello:
        (is_hello, num_chunks) = wait_hello(nrf)
        if not is_hello:
            print("Waiting again for hello...")
    
    # At this point a positive ack has been sent
#    ioparent.control_led(1, True)
#    ioparent.control_led(3, True)

    for i in range(num_chunks):
        
        # LEDs 3, 4 and 5 will indicate the received percentage
#        if i > 2*num_chunks/3: 
#            ioparent.control_led(4, True)
#        elif i >= num_chunks - 1:
#            ioparent.control_led(5, True)


        chunk_data = bytearray()
        # Wait for chunk_info until we receive a chunk_info packet
        is_chunk_info = False
        while not is_chunk_info:
            (is_chunk_info, num_subchunks) = wait_chunk_info(nrf, i)
            if not is_chunk_info:
                print("Packet received is not a chunk info packet. Waiting again for chunk info packet...")

            # Check that the chunk that is going to be received corresponds to the chunk expected 
                
        # Start receiving data  packets of chunk i
        for subchunk_id in range(num_subchunks):
            is_data_frame = False
            while not is_data_frame:
                (is_data_frame, data) = wait_data_frame(nrf, subchunk_id)
                if not is_data_frame:
                    print("Waiting again for data frame...")
                # Logging message
                if (subchunk_id != 0) and (not subchunk_id%10):
                    print("Received until subchunk " + str(subchunk_id))
            
            # Data is good. Add the data to the chunk data bytearray
            chunk_data.extend(data)
        
        # All subchunks of chunk have been received. If decompression is good save to file, if not ask to send again chunk 
        print("------------chunk id: " + str(i) + "----------------")
        chunk_correct = True
        try:    
            decompressed_chunk = chunk_handler.decompress_chunk(chunk_data)
        except:
            # Decompression failed -> Chunk has errors, ask to retransmit chunk
            chunk_correct = False
        is_chunk_is_good = False
        while not is_chunk_is_good:
            is_chunk_is_good = wait_chunk_is_good(nrf, chunk_correct, id)
            if not is_chunk_info:
                print("Waiting for chunk_is_good frame again...")

        if not chunk_correct:
            # We expect to receive again last frame
            i = i - 1
        else:
            # Chunk was correct we write it to file
            write_chunk_to_file(filename, decompressed_chunk)     

    print("All data has been received correctly, copying file to usb")
#    ioparent.control_led(0, False)
    subprocess.call("./write_usb.sh")


def setup_receiver():
    print("Setting up the NRF24 configuration")

    hostname = "localhost"
    port = 8888
    address = p_utils.ADDRESS

    pi = p_utils.connect_to_gpio(hostname, port)

    nrf = create_receiver_nrf(pi, address)

    return nrf


def create_receiver_nrf(pi, address):
    # Create NRF24 object.
    # PLEASE NOTE: PA level is set to MIN, because test sender/receivers are often close to each other, and then MIN works better.
    # ALSO NOTE: pauload size is set to ACK. That means that payload is variable and acks can contain payload as well
    nrf = NRF24(pi, ce=25, spi_speed=constants.SPI_SPEED, payload_size=constants.PAYLOAD_SIZE, channel=constants.CHANNEL, data_rate=constants.DATA_RATE, pa_level=constants.PA_LEVEL)
    nrf.set_address_bytes(len(address))

    # Listen on the address specified as parameter
    nrf.open_reading_pipe(RF24_RX_ADDR.P1, address)
    
    # Display the content of NRF24L01 device registers.
    nrf.show_registers()

    return nrf

def wait_hello(nrf: NRF24):

    # Set a positive payload for the next ack
    set_next_ack(nrf, True, 0, 0)

    wait_data(nrf)
    
    # Data is available, check it is hello frame
    payload = nrf.get_payload()
    if payload[0] != 0x00:
        print("Frame received is not a hello frame: payload[0] = " + str(payload[0]))
        return (False, -1)

    num_chunks = int.from_bytes([payload[1], payload[2]], "little")
    print("Hello frame received -> num of chunks: " + str(num_chunks))

    return (True, num_chunks)

def wait_chunk_info(nrf: NRF24, id): 

    # Set a positive payload for the next ack
    set_next_ack(nrf, True, 1, id)
    wait_data(nrf)

    # Data is available, check it is chunk_info frame
    payload = nrf.get_payload()
    if payload[0] != 1:
        print("Frame received is not a chunk info frame: payload[0] = " + str(payload[0]))
        return (False, -1)

    # Get chunk info data
    subchunks_num = int.from_bytes([payload[1], payload[2]], "little")
    chunk_id = payload[3] 

    print("Chunk_info received -> Chunk id: " + str(chunk_id) + ", num of subchunks: " + str(subchunks_num))

    # Ensure that the chunk info received corresponds to the one expected
    if id != chunk_id:
        print("Chunk doesn't correspond to the expected chunk: expected = " + str(id) + ", received = " + str(chunk_id))
        return (False, -1)

    return (True, subchunks_num)

def wait_data_frame(nrf: NRF24, id: int):
    # Returns False if it is not a data frame type or it doesn't correspond to the id expected
    # If everything alright returns the data

    # Set a positive payload for the next ack
    set_next_ack(nrf, True, 2, id)

    wait_data(nrf)

    # Data is available, check it is data frame
    # Get data type from byte

    payload = nrf.get_payload()
    type = get_type_from_byte(payload[0])
    received_id = get_id_from_byte(payload[0])
    if type != 0x02:
        print("Frame received is not a data frame: payload[0] = " + str(payload[0]))
        return (False, -1)
    
    if received_id != id: 
        print("Data received doesn't correspond to data frame id expected: expected = " + str(id) + ", received=" + str(received_id))
        return (False, -1)

    # Get data (bytes from position 1 until end)
    data = payload[1:32]
    return (True, data)

def get_type_from_byte(first_b : int):
    # We return the left 4 bits of the byte -> 10111011 & 11110000 = 10110000
    return first_b >> 4

def get_id_from_byte(first_b : int):
    # We return the right 4 bits of the byte -> 10111011 & 00001111 = 00001011
    return first_b & 15

def wait_chunk_is_good(nrf: NRF24, good: bool, id: int): 

    wait_data(nrf)

    # Data is available, check it is chunk_info frame
    payload = nrf.get_payload()
    if payload[0] != 3:
        print("Frame received is not a chunk_is_good frame: payload[0] = " + str(payload[0]))
        if payload[0] == 2:
            print("Received data frame returning true")
            set_next_ack(nrf, True, 3, id)
        return False

    # Get the chunk id
    chunk_id = int.from_bytes([payload[1], payload[2]], "little")

    print("Chunk_is_good Frame received -> chunk_id : " + str(chunk_id))
    if id != chunk_id:
        print("Received id in chunk_is_good is from another id -> Expected id: " + str(id) + ", Received id: " + str(chunk_id))
        return (False, -1)

    # Set a positive payload for the next ack
    print("Setting next ack to negative. For testing purposes")
    set_next_ack(nrf, False, 3, id)
    
    return True

def set_next_ack(nrf: NRF24, positive, type: int, id: int):
    if positive:
        nrf.ack_payload(RF24_RX_ADDR.P1, [(1).to_bytes(1, "big"), type.to_bytes(1, "big"), id.to_bytes(1, "big")])
    else:
        nrf.ack_payload(RF24_RX_ADDR.P1, [(0).to_bytes(1, "big"), type.to_bytes(1, "big"), id.to_bytes(1, "big")])

def wait_data(nrf: NRF24):
    # print("Waiting for new data...")
    while not nrf.data_ready():
        time.sleep(constants.RETRY_DELAY)

def clean_working_dir(filename):
    try:
        os.remove(filename)
    except:
        # Directory already clean
        return

def write_chunk_to_file(filename, chunk):
    f = open(filename, "ab")
    f.write(chunk)
    f.close()



if __name__ == "__main__":
    start_receiver()