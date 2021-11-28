# General import
import subprocess
import time
from datetime import datetime
import os
import sys

# Local files imports
import chunk_handler
import packet_creator
import utils

# nrf24 library import
import RF24



def start_sender(chunk_size):
    print("Starting sender")
    time_start = time.time()

    # Setup nrf24 sender
    radio = setup_sender()

    # Copy file from USB to working directory
    subprocess.call("./read_usb.sh")

    # Get file from working directory
    filename = get_file_from_working_dir()

    # Get file chunks
    chunks = chunk_handler.get_file_chunks(filename, utils.CHUNKS_SIZE)
    subchunks = packet_creator.create_data_frames(chunks)

    # Send Hello frame
    send_hello(radio, len(chunks))
    # Start sending the data frames
    # For each chunk we send a chunk_info frame with the number of subchunks and the chunk id
    # To start sending the subchunks we must receive a positive ack to the chunk_info frame
    return
    for chunk_id in range(len(chunks)):
        subchunk_num = len(subchunks[chunk_id])
        ready = False
        while not ready:
            if not send_chunk_info(nrf, subchunk_num, chunk_id):
                # TODO: delete this while
                # Receiver is not ready yet or the ack has been lost. Wait and try again
                print("Positive ack not received to chunk_info frame, sending again...")
                time.sleep(constants.RETRY_DELAY)
            else:
                ready = True
        # Receiver is ready to receive the data frames
        for subchunk in subchunks[chunk_id]:
            ready = False
            while not ready:
                if not send_subchunk(nrf, subchunk):
                    print("Positive ack not received to data frame, sending again...")
                    time.sleep(constants.RETRY_DELAY)
                else:
                    ready = True
    print("Reached end of program. In theory all data has been sent correctly")
    time_end = time.time()
    print("Time elapsed: " + str(time_end - time_start))

def get_file_from_working_dir() -> str:

    # Get list of files in working directory
    files = [f for f in os.listdir(utils.WORKING_DIR) if os.path.isfile(os.path.join(utils.WORKING_DIR, f))]

    # We will send only one file
    if len(files) == 0:
        print("No files found in the working directory. Aborting...")
        sys.exit()
    filename = os.path.join(utils.WORKING_DIR, files[0])

    print("File to send: " + filename)
    return filename

def setup_sender():

    print("Setting up the NRF24 configuration")

    radio = RF24.RF24(utils.SPI_SPEED)
    radio.begin(utils.CE_PIN, utils.IRQ_PIN) #Set CE and IRQ pins
    radio.setPALevel(utils.PA_LEVEL)
    radio.setDataRate(utils.DATA_RATE)
    radio.setChannel(utils.CHANNEL)
    radio.setRetries(utils.RETRY_DELAY,utils.RETRY_COUNT)

    radio.enableDynamicPayloads()  
    radio.enableAckPayload()

    radio.openWritingPipe(utils.TX_WRITE_PIPE)
    radio.openReadingPipe(1, utils.RX_WRITE_PIPE)

    radio.powerUp()
    radio.printPrettyDetails()

    radio.stopListening()  # put radio in TX mode
    return radio

def send_hello(radio: RF24, chunk_num: int) -> bool:
    # Sends the hello frame, waits for the ack and checks that it is positive
    # If everything is successful returns true

    # Create and send hello frame
    payload = packet_creator.create_hello_frame(chunk_num)
    send_infinity(radio, payload, True) # We want to retry until we receive a positive ack

def send_infinity(radio, payload, check_ack_is_positive):
    attempt = 1

    success, ack_payload = send(radio, payload)
    is_positive = True
    if check_ack_is_positive:
        is_positive = is_ack_positive(ack_payload)    
    while not success or not is_positive: 
        print("Retrying. Attempt: " + str(attempt))
        success, ack_payload = send(radio, payload)
        time.sleep(utils.RETRY_DELAY)
    return ack_payload

def send(radio, payload):
    
    if radio.write(payload): # Sends and waits ack (2 layer OSI retries included)
        print("Success")
        has_payload, pipe_number = radio.available_pipe()
        if has_payload:
            print("Has payload")
            length = radio.getDynamicPayloadSize()
            return (True, radio.read(length))
        else:
            print("Empty ACK")
            return (False, -1)
    else:
        print("Failed")
        return (False, -1)

def send_chunk_info(nrf: RF24, subchunk_num, chunk_id):
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
            time.sleep(utils.RETRY_DELAY)
            attempt += 1
        
        else: 
            attempt = 0

    return is_ack_positive(ack_payload)

def send_subchunk(nrf: RF24, subchunk):
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

        # Check if ACK is positive
        (ack_received, ack_payload) = get_ack_payload(nrf)

        if not ack_received:
            print("  * ACK for data frame not received. Retrying transmission. Attempt: " + str(attempt))
            time.sleep(constants.RETRY_DELAY)
            attempt += 1
        
        else: 
            attempt = 0

    return is_ack_positive(ack_payload)


def get_ack_payload(nrf: RF24):
    # Check if an acknowledgement package is available.
    if nrf.data_ready():
        # Get payload.
        payload = nrf.get_payload()
        #print("ACK payload: " + str(payload))
        return (True, payload)

    else:
        # print("No acknowledgement payload package received.")å
        # TODO: Handle this case when the ack doesn't arrive 
        return (False, -1)

def is_package_lost(nrf: RF24):
    # Returns true if package has been lost

    if nrf.get_packages_lost() != 0:
        print("Package is lost")
        return True
    return False

def is_ack_positive(ack_payload):
    try:
        if ack_payload[0] == 1:
            # print("Checking ack -> Positive")
            return True
    except:
        return False
    return False


if __name__ == "__main__":
    start_sender(10)