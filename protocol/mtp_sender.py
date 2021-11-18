# Local files imports
import chunk_handler
import packet_creator
import protocol_utils as p_utils

# nrf24 library import
from nrf24 import *

# General imports
import sys
import time


def start_sender():
    print("Starting sender")

    # Setup nrf24 sender
    global nrf
    nrf = setup_sender()

    # Get file chunks
    chunks = chunk_handler.get_file_chunks("small.txt", 2)
    subchunks = packet_creator.create_data_frames(chunks)

    # Send Hello frame
    if not send_hello(len(chunks)):
        # Hello didn't work 
        # TODO: Handle this case
        print("Hello didn't work. Aborting...")
        sys.exit()

    # Start sending the data frames
    # For each chunk we send a chunk_info frame with the number of subchunks and the chunk id
    # To start sending the subchunks we must receive a positive ack to the chunk_info frame
    for chunk_id in range(len(chunks)):
        subchunk_num = len(subchunks[chunk_id])
        ready = False
        while not ready:
            if not send_chunk_info(subchunk_num, chunk_id):
                # Receiver is not ready yet. Wait and try again
                time.sleep(1)
                ready = False
            else:
                ready = True
        # Receiver is ready to receive the data frames
        for subchunk in subchunks[chunk_id]:
            if not send_subchunk(subchunk):
                # TODO: handle data frame didn't work
                sys.exit()

    print("Reached end of program. In theory all data has been sent correctly")

def setup_sender():
    print("Setting up the NRF24 configuration")

    hostname = "localhost"
    port = 8888
    address = p_utils.ADDRESS

    pi = p_utils.connect_to_gpio(hostname, port)

    nrf = create_sender_nrf(pi, address)

    return nrf

def create_sender_nrf(pi, address):
    # Create NRF24 object.
    # PLEASE NOTE: PA level is set to MIN, because test sender/receivers are often close to each other, and then MIN works better.
    nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.ACK, channel=100, data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.LOW)
    nrf.set_address_bytes(len(address))
    nrf.set_retransmission(15, 15)
    nrf.open_writing_pipe(address)
    
    # Display the content of the nrf24 device registers.
    nrf.show_registers()

    return nrf

def send_hello(chunk_num: int):
    # Sends the hello frame, waits for the ack and checks that it is positive
    # If everything is successful returns true

    print("Sending hello frame")
    # Create and send hello frame
    payload = packet_creator.create_hello_frame(chunk_num)
    if not send(payload):
        # TODO: Handle case when timeout is exceeded
        sys.exit()

    # Get ACK
    if is_package_lost():
        # TODO: Handle package is lost
        sys.exit()

    # Check if ack is positive
    return is_ack_positive(get_ack_payload())


def send_chunk_info(subchunk_num, chunk_id):
    # Sends the chunk info frame, waits for the ack and checks that is it positive
    # If everything is successful returns true

    print("Sending chunk info frame")
    # Create and send chunk_info frame
    payload = packet_creator.create_chunk_info_frame(subchunk_num, chunk_id)

    if not send(payload):
        # TODO: Handle case when timeout is exceeded
        sys.exit()

    # Get ACK
    if is_package_lost():
        # TODO: Handle package is lost
        sys.exit()

    # Check if ACK is positive
    return is_ack_positive(get_ack_payload())

def send_subchunk(subchunk):
    # Sends a subchunk data frame, waits for the ack
    # If everything is successful returns true
    if not send(subchunk):
        # TODO: Handle case when timeout is exceeded
        sys.exit()

    # Get ACK
    if is_package_lost():
        # TODO: Handle package is lost
        sys.exit()

    # Check if ACK is positive
    return is_ack_positive(get_ack_payload())

def send(payload) -> bool:
    # Sends the a packet and waits until it is sent
    # If timeout exideed returns False, True otherwise
    
    nrf.reset_packages_lost()
    nrf.send(payload)

    # Wait for transmission to complete.
    timeout = False
    try:
        nrf.wait_until_sent()
    except TimeoutError:
        print("Timeout exceeded to send a packet")
        timeout = True
    return not timeout

def get_ack_payload():
    # Check if an acknowledgement package is available.
    if nrf.data_ready():
        # Get payload.
        payload = nrf.get_payload()
        print("ACK payload: " + payload)

    else:
        print("No acknowledgement package received.")
        # TODO: Handle this case when the ack doesn't arrive 

def is_package_lost():
    # Returns true if package has been lost

    if nrf.get_packages_lost() != 0:
        print("Package is lost")
        return True
    return False

def is_ack_positive(ack_payload):

    if ack_payload[0] == '0x01':
        return True

    return False
