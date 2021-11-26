# Local files imports
import chunk_handler
import packet_creator
import protocol_utils as p_utils

# nrf24 library import
from nrf24 import *
import constants

# General imports
import subprocess
import time
from datetime import datetime
import os
import sys
#import ioparent


def start_sender():
    print("Starting sender")
    #ioparent.control_led(1, True)
    time_start = time.time()

    # Setup nrf24 sender
    nrf = setup_sender()

    # Copy file from USB to working directory
    subprocess.call("./read_usb.sh")

    # Get file from working directory
    filename = get_file_from_working_dir()

    # Get file chunks
    chunks = chunk_handler.get_file_chunks(filename, constants.CHUNK_SIZE)
    subchunks = packet_creator.create_data_frames(chunks)

    # Send Hello frame
    ready = False
    while not ready:
        if not send_hello(nrf, len(chunks)):
            # Hello didn't work 
            print("Hello didn't work. Sending again hello package...")
        else:
            ready = True

    # Start sending the data frames
    # For each chunk we send a chunk_info frame with the number of subchunks and the chunk id
    # To start sending the subchunks we must receive a positive ack to the chunk_info frame
    for chunk_id in range(len(chunks)):
        subchunk_num = len(subchunks[chunk_id])
        ready = False
        while not ready:
            # TODO: Make chunk_id module 255 for the 8 bits
            if not send_chunk_info(nrf, subchunk_num, chunk_id):
                # TODO: delete this while
                # Receiver is not ready yet or the ack has been lost. Wait and try again
                print("Received ack doesn't correspond to the sent frame. Sending again...")
                time.sleep(constants.RETRY_DELAY)
            else:
                ready = True
        # Receiver is ready to receive the data frames
        subchunk_id = 0
        for subchunk in subchunks[chunk_id]:
            ready = False
            while not ready:
                if not send_subchunk(nrf, subchunk, subchunk_id):
                    print("ACK received doesn't correspond to the sended frame, sending again...")
                    time.sleep(constants.RETRY_DELAY)
                else:
                    ready = True
            subchunk_id = subchunk_id + 1

        if not send_chunk_is_good(nrf, chunk_id):
            # Receiver needs to receive the chunk again
            print("Chunk was not good, sending again chunk with id: " + str(chunk_id))
            chunk_id = chunk_id - 1

    print("Reached end of program. In theory all data has been sent correctly")
    time_end = time.time()
    print("Time elapsed: " + str(time_end - time_start))
#   ioparent.control_led(1, False)

def get_file_from_working_dir() -> str:

    # Get list of files in working directory
    files = [f for f in os.listdir(p_utils.WORKING_DIR) if os.path.isfile(os.path.join(p_utils.WORKING_DIR, f))]

    # We will send only one file
    if len(files) == 0:
        print("No files found in the working directory. Aborting...")
        sys.exit()
    filename = os.path.join(p_utils.WORKING_DIR, files[0])

    print("File to send: " + filename)
    return filename

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
    nrf = NRF24(pi, ce=25, spi_speed=constants.SPI_SPEED, payload_size=constants.PAYLOAD_SIZE, channel=constants.CHANNEL, data_rate=constants.DATA_RATE, pa_level=constants.PA_LEVEL)
    nrf.set_address_bytes(len(address))
    nrf.set_retransmission(1, 15)
    nrf.open_writing_pipe(address)
    
    # Display the content of the nrf24 device registers.
    nrf.show_registers()

    return nrf

def send_hello(nrf: NRF24, chunk_num: int) -> bool:
    # Sends the hello frame, waits for the ack and checks that it is positive
    # If everything is successful returns true

    # Create and send hello frame
    payload = packet_creator.create_hello_frame(chunk_num)
    print("Sending hello frame -> num of chunks: " + str(chunk_num))
    attempt = 1
    while attempt != 0:
        if not send(nrf, payload):
            # TODO: Handle case when timeout is exceeded
            print("  * Timeout sending hello frame. Retrying transmission. Attempt: " + str(attempt))
            attempt += 1

        # Get ACK
        # if is_package_lost(nrf):
        #     # TODO: Handle package is lost
        #     print("  * Hello frame lost. Retrying transmission. Attempt: " + str(attempt))
        #     attempt += 1

        (ack_received, ack_payload) = get_ack_payload(nrf)

        if not ack_received:
            print("  * ACK for hello frame not received. Retrying transmission. Attempt: " + str(attempt))
            time.sleep(constants.RETRY_DELAY)
            attempt += 1
        
        else: 
            attempt = 0

    # Hello frame is always type=0 and id=0
    return check_expected_ack(ack_payload, 0, 0)

def send_chunk_info(nrf: NRF24, subchunk_num, chunk_id):
    # Sends the chunk info frame, waits for the ack and checks that is it positive
    # If everything is successful returns true

    # Create and send chunk_info frame
    payload = packet_creator.create_chunk_info_frame(subchunk_num, chunk_id)
    print("Sending chunk info frame -> chunk id: " + str(chunk_id) + ", num of subchunks: " + str(subchunk_num))

    attempt = 1
    while attempt:
        if not send(nrf, payload):
            # TODO: Handle case when timeout is exceeded
            print("  * Timeout sending chunk info frame. Retrying transmission. Attempt: " + str(attempt))
            attempt += 1

        # Get ACK
        # if is_package_lost(nrf):
        #     # TODO: Handle package is lost
        #     print("  * Chunk info frame lost. Retrying transmission. Attempt: " + str(attempt))
        #     attempt += 1

        # Check if ACK is positive
        (ack_received, ack_payload) = get_ack_payload(nrf)

        if not ack_received:
            print("  * ACK for chunk info frame not received. Retrying transmission. Attempt: " + str(attempt))
            time.sleep(constants.RETRY_DELAY)
            attempt += 1
        
        else: 
            attempt = 0

    return check_expected_ack(ack_payload, 1, chunk_id)

def send_subchunk(nrf: NRF24, subchunk, subchunk_id):
    # Sends a subchunk data frame, waits for the ack
    # If everything is successful returns true

    # print("Sending data frame")
    
    attempt = 1
    while attempt:
        if not send(nrf, subchunk):
            # TODO: Handle case when timeout is exceeded
            print("  * Timeout sending data frame. Retrying transmission. Attempt: " + str(attempt))
            attempt += 1

        # Get ACK
        # if is_package_lost(nrf):
        #     # TODO: Handle package is lost
        #     print("  * Data frame lost. Retrying transmission. Attempt: " + str(attempt))
        #     attempt += 1

        (ack_received, ack_payload) = get_ack_payload(nrf)

        if not ack_received:
            print("  * ACK for data frame not received. Retrying transmission. Attempt: " + str(attempt))
            time.sleep(constants.RETRY_DELAY)
            attempt += 1
        
        else: 
            attempt = 0

    return check_expected_ack(ack_payload, 2, subchunk_id)

def send_chunk_is_good(nrf: NRF24, chunk_id: int):
    print("Asking if chunk has been good")

    payload = packet_creator.create_chunk_is_good_frame(chunk_id)
    attempt = 1
    while attempt:
        if not send(nrf, payload):
            # TODO: Handle case when timeout is exceeded
            print("  * Timeout sending data frame. Retrying transmission. Attempt: " + str(attempt))
            attempt += 1

        # Get ACK
        # if is_package_lost(nrf):
        #     # TODO: Handle package is lost
        #     print("  * Data frame lost. Retrying transmission. Attempt: " + str(attempt))
        #     attempt += 1

        (ack_received, ack_payload) = get_ack_payload(nrf)

        if not ack_received:
            print("  * ACK for data frame not received. Retrying transmission. Attempt: " + str(attempt))
            time.sleep(constants.RETRY_DELAY)
            attempt += 1
            continue

        if not check_expected_ack(ack_payload, 3, chunk_id):
            attempt += 1
            continue

        else: 
            attempt = 0

    return is_ack_positive(ack_payload)
def send(nrf: NRF24, payload) -> bool:
    # Sends the a packet and waits until it is sent
    # If timeout exideed returns False, True otherwise
    # print("")
    # print("BEFORE SEND: ", datetime.now())
    nrf.reset_packages_lost()
    nrf.send(payload)

    # Wait for transmission to complete.
    timeout = False
    # try:
    #     nrf.wait_until_sent()
    # except TimeoutError:
    #     print("Timeout exceeded to send a packet")
    #     timeout = True
    # print("AFTER SEND: ", datetime.now())
    return not timeout

def get_ack_payload(nrf: NRF24):
    # Check if an acknowledgement package is available.
    time.sleep(constants.RETRY_DELAY)
    for i in range(constants.ACK_WAIT_TIMEOUT):
        if nrf.data_ready():
            # Get payload.
            payload = nrf.get_payload()
            #print("ACK payload: " + str(payload))
            return (True, payload)

        #print("No acknowledgement payload package received. Waiting again...")
    print("ACK timeout exceeded")
    return (False, -1)

def is_package_lost(nrf: NRF24):
    # Returns true if package has been lost

    if nrf.get_packages_lost() != 0:
        print("Package is lost")
        return True
    return False

def is_ack_positive(ack_payload):
    if ack_payload[0] == 1:
        # print("Checking ack -> Positive")
        return True

    print("Checking ack -> Negative")
    return False

def check_expected_ack(ack_payload, type, id):
    if ack_payload[1] != type or ack_payload[2] != id:
        print("ACK doesn't correspond to the expected one")
        return False

if __name__ == "__main__":
    start_sender()