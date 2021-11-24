# local imports 
import protocol_utils as p_utils
import chunk_handler
import ioparent

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

    # Wait for Hello frame
    (is_hello, num_chunks) = wait_hello(nrf)
    if not is_hello:
        # TODO: handle case when first packet received is not a hello frame
        sys.exit()
    
    # At this point a positive ack has been sent
    ioparent.control_led(1, True)
    ioparent.control_led(3, True)

    for i in range(num_chunks):
        
        # LEDs 3, 4 and 5 will indicate the received percentage
        if i > 2*num_chunks/3: 
            ioparent.control_led(4, True)
        elif i >= num_chunks - 1:
            ioparent.control_led(5, True)


        chunk_data = bytearray()
        # Wait for chunk_info
        is_chunk_info = False
        while not is_chunk_info:
            (is_chunk_info, num_subchunks, chunk_id) = wait_chunk_info(nrf)
            if not is_chunk_info:
                # TODO: handle case when second packet received is not a chunk info frame
                print("Packet received is not a chunk info packet. Waiting again for chunk info packet...")
                
        
        # Check that the chunk that is going to be received corresponds to the chunk expected 
        if i != chunk_id:
            print("Chunk doesn't correspond to the expected chunk: expected = " + str(i) + ", received = " + str(chunk_id))
            # TODO: handle case when chunk received doesn't correspond to the expected one
            sys.exit()

        for subchunk_id in range(num_subchunks):
            (is_data_frame, data) = wait_data_frame(nrf)
            if not is_data_frame:
                # TODO: handle case when packet received is not a data frame
                sys.exit()
            
            if (subchunk_id is not 0) and (not subchunk_id%10):
                print("Received until subchunk " + str(subchunk_id))
            
            # Add the data to the chunk data bytearray
            chunk_data.extend(data)
        
        # We don't set the following ack to positive to ensure that sender waits until decompression and writing is finished

        # All subchunks of chunk have been received. Decompress and save to file
        # for testing purposes we just print it to console
        print("------------chunk id: " + str(chunk_id) + "----------------")
        decompressed_chunk = chunk_handler.decompress_chunk(chunk_data)
        # print(decompressed_chunk)
        write_chunk_to_file(filename, decompressed_chunk)        

    print("All data has been received correctly, copying file to usb")
    ioparent.control_led(0, False)
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
    set_next_ack(nrf, True)
    wait_data(nrf)
    
    # Data is available, check it is hello frame
    payload = nrf.get_payload()
    if payload[0] != 0x00:
        print("Frame received is not a hello frame: payload[0] = " + str(payload[0]))
        return (False, -1)

    num_chunks = int.from_bytes([payload[1], payload[2]], "little")
    print("Hello frame received -> num of chunks: " + str(num_chunks))

    return (True, num_chunks)

def wait_chunk_info(nrf: NRF24): 

    # Set a positive payload for the next ack
    set_next_ack(nrf, True)
    wait_data(nrf)

    # Data is available, check it is chunk_info frame
    payload = nrf.get_payload()
    if payload[0] != 0x01:
        print("Frame received is not a chunk info frame: payload[0] = " + str(payload[0]))
        return (False, -1, -1)

    # Get subchunks ammount (bytes at position 1 and 2)
    #subchunks_num = int.from_bytes(payload[1].to_bytes(1, 'big') + payload[2].to_bytes(1, 'big'), 'big')
    #chunk_id = payload[3]

    # Temporal workaround while create_chunk_info_frame() is not working properly
    subchunks_num = int.from_bytes([payload[1], payload[2]], "little")
    chunk_id = payload[3] 

    print("Chunk_info received -> Chunk id: " + str(chunk_id) + ", num of subchunks: " + str(subchunks_num))
    
    return (True, subchunks_num, chunk_id)

def wait_data_frame(nrf: NRF24):
    print("")
    print("ENTERING wait_data_frame: ", datetime.now())
    # Set a positive payload for the next ack
    set_next_ack(nrf, True)
    print("ACK SET: ", datetime.now())

    wait_data(nrf)
    print("DATA RECEIVED", datetime.now())
    # Data is available, check it is data frame
    payload = nrf.get_payload()
    if payload[0] != 0x02:
        print("Frame received is not a data frame: payload[0] = " + str(payload[0]))
        return (False, -1)
    print("PAYLOAD READ: ", datetime.now())

    # Get data (bytes from position 1 until end)
    data = payload[1:32]
    return (True, data)

def set_next_ack(nrf: NRF24, positive):
    if positive:
        nrf.ack_payload(RF24_RX_ADDR.P1, bytes([1]))
    else:
        nrf.ack_payload(RF24_RX_ADDR.P1, bytes([0]))

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