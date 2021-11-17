# local imports 
import protocol_utils as p_utils
import chunk_handler

# nrf24 library import
from nrf24 import *

# general imports
import time
import sys

def start_receiver():
    print("Starting receiver")
    # Setup nrf24
    global nrf
    nrf = setup_receiver()

    # Wait for Hello frame
    (is_hello, num_chunks) = wait_hello()
    if not is_hello:
        # TODO: handle case when first packet received is not a hello frame
        sys.exit()
    
    # At this point a positive ack has been sent

    for i in range(num_chunks):
        chunk_data = bytearray()
        # Wait for chunk_info
        (is_chunk_info, num_subchunks, chunk_id) = wait_chunk_info()
        if not is_chunk_info:
            # TODO: handle case when second packet received is not a chunk info frame
            sys.exit()
        
        # We set the following acks to negative ack to ensure the next chunk_info is avoided
        set_next_acks(False)
        
        # Check that the chunk that is going to be received corresponds to the chunk expected 
        if i != chunk_id:
            print("Chunk doesn't correspond to the expected chunk: expected = " + str(i) + ", received = " + str(chunk_id))
            # TODO: handle case when chunk received doesn't correspond to the expected one
            sys.exit()

        for subchunk_id in range(num_subchunks):
            (is_data_frame, data) = wait_data_frame()
            if not is_data_frame:
                # TODO: handle case when packet received is not a data frame
                sys.exit()
            
            # Add the data to the chunk data bytearray
            chunk_data.append(data)
        
        # All subchunks of chunk have been received. Decompress and save to file
        # for testing purposes we just print it to console
        print("------------chunk id: " + chunk_id + "----------------")
        print(chunk_handler.decompress_chunk(chunk_data))


def setup_receiver():
    print("Setting up the NRF24 configuration")

    hostname = "localhost"
    port = 8888
    address = p_utils.ADDRESS

    pi = p_utils.connect_to_gpio(hostname, port)

    nrf = create_receiver_nrf(pi, address)

    # Set as the next ack payload a positive ack payload

    return nrf


def create_receiver_nrf(pi, address):
    # Create NRF24 object.
    # PLEASE NOTE: PA level is set to MIN, because test sender/receivers are often close to each other, and then MIN works better.
    # ALSO NOTE: pauload size is set to ACK. That means that payload is variable and acks can contain payload as well
    nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.ACK, channel=100, data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.MIN)
    nrf.set_address_bytes(len(address))

    # Listen on the address specified as parameter
    nrf.open_reading_pipe(RF24_RX_ADDR.P1, address)
    
    # Set a positive payload for the next ack
    set_next_acks(True)

    # Display the content of NRF24L01 device registers.
    nrf.show_registers()

    return nrf

def wait_hello():

    wait_data()
    
    # Data is available, check it is hello frame
    payload = nrf.get_payload()
    if payload[0] != 0x00:
        print("Frame received is not a hello frame")
        return (False, -1)
    num_chunks = payload[1]

    return (True, num_chunks)

def wait_chunk_info(): 

    wait_data()

    # Data is available, check it is chunk_info frame
    payload = nrf.get_payload()
    if payload[0] != 0x01:
        print("Frame received is not a chunk info frame")
        return (False, -1, -1)

    # Get subchunks ammount (bytes at position 1 and 2)
    subchunks_num = int.from_bytes(payload[1].to_bytes(1, 'big') + payload[2].to_bytes(1, 'big'), 'big')
    chunk_id = payload[3] 
    
    return (True, subchunks_num, chunk_id)

def wait_data_frame():

    wait_data()

    # Data is available, check it is data frame
    payload = nrf.get_payload()
    if payload[0] != 0x02:
        print("Frame received is not a data frame")
        return (False, -1)

    # Get data (bytes from position 1 until end)
    data = payload[1:32]
    
    return (True, data)

def set_next_acks(positive):
    if positive:
        nrf.ack_payload(RF24_RX_ADDR.P1, bytes(b'0x01'))
    else:
        nrf.ack_payload(RF24_RX_ADDR.P1, bytes(b'0x00'))

def wait_data():
    while not nrf.data_ready():
        time.sleep(0.01)