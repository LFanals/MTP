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
import ioparent

# nrf24 library import
import RF24

def start_sender(mode):
    print("Starting sender")
    time_start = time.time()
    set_global_config(mode)

    # Setup nrf24 sender
    radio = setup_sender()

    # Copy file from USB to working directory
    subprocess.call(utils.MTP_DIR + "read_usb.sh")

    # Get file from working directory
    filename = get_file_from_working_dir()

    # Get file chunks
    chunks = chunk_handler.get_file_chunks(filename, config.CHUNKS_SIZE, config.COMPRESSION_LEVEL)
    subchunks = packet_creator.create_data_frames(chunks)

    # Send Hello frame
    num_chunks = len(chunks)
    send_hello(radio, num_chunks)

    # Start sending the data frames
    chunk_id = 0
    blink_led = True

    while chunk_id < num_chunks:
        # check if master switch is still ON
        if not ioparent.is_master_on():
            return 1

        ioparent.update_led_percentage(chunk_id, num_chunks)
        chunk_is_good = False
        subchunk_num = len(subchunks[chunk_id])
        send_chunk_info(radio, subchunk_num, chunk_id)
        print("\n________________________________")
        print("Sending chunk ", chunk_id)
        
        # Receiver is ready to receive the data frames
        count = 0
        for subchunk in subchunks[chunk_id]:
            send_subchunk(radio, subchunk)
            count = count + 1
            if count !=0 and count % 200 == 0: 
                print("  + Sent until subchunk " + str(count))
                ioparent.control_led(1, blink_led)
                blink_led = not blink_led


        chunk_is_good, expected_id = send_chunk_is_good(radio, chunk_id)
        if not chunk_is_good:
            print("Chunk was not good sending again chunk id: " + str(expected_id))
            chunk_id = expected_id
        elif chunk_id + 1 != num_chunks:
            chunk_id = chunk_id + 1
            print("Chunk was good, sending next.")
        else:
            chunk_id = chunk_id + 1
            print("Last chunk sent, ending TX")

    print("Reached end of program. In theory all data has been sent correctly")
    ioparent.control_led(1, False)
    time_end = time.time()
    print("Time elapsed: " + str(time_end - time_start))
    return 0



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

    radio = RF24.RF24(config.SPI_SPEED)
    radio.begin(utils.CE_PIN, utils.IRQ_PIN) #Set CE and IRQ pins
    radio.setPALevel(config.PA_LEVEL)
    radio.setDataRate(config.DATA_RATE)
    radio.setChannel(config.CHANNEL)
    radio.setRetries(config.RETRY_DELAY,config.RETRY_COUNT)

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

    payload = packet_creator.create_hello_frame(chunk_num)
    print("Sending Hello frame -> num of chunks: " + str(chunk_num))
    send_infinity(radio, payload, True)


def send_chunk_info(radio: RF24, subchunk_num, chunk_id):
    # Sends the chunk info frame, waits for the ack and checks that is it positive
    # If everything is successful returns true

    payload = packet_creator.create_chunk_info_frame(subchunk_num, chunk_id)
    print("Sending chunk info frame -> chunk id: " + str(chunk_id) + ", num of subchunks: " + str(subchunk_num))
    send_infinity(radio, payload, True)

def send_subchunk(radio: RF24, subchunk):
    send_infinity(radio, subchunk, False)

def send_chunk_is_good(radio: RF24, chunk_id):

    print("Sending chunk is good frame -> chunk id: " + str(chunk_id))
    payload = packet_creator.create_chunk_is_good_frame(chunk_id)
    ack_payload = send_infinity(radio, payload, False)
    return (is_ack_positive(ack_payload), get_expected_chunk_id(ack_payload))

def is_ack_positive(ack_payload):
    try:
        if ack_payload[0] == 1:
            return True
    except:
        return False
    return False

def get_expected_chunk_id(ack_payload):
    return ack_payload[1]


def send_infinity(radio, payload, check_ack_is_positive):
    attempt = 1

    success, ack_payload = send(radio, payload)
    is_positive = True

    if check_ack_is_positive:
        is_positive = is_ack_positive(ack_payload)    

    while not success or not is_positive: 
        print("Retrying. Attempt: " + str(attempt))
        success, ack_payload = send(radio, payload)
        if check_ack_is_positive:
            is_positive = is_ack_positive(ack_payload)    
        attempt = attempt + 1
        time.sleep(config.SLEEP_DELAY)
    return ack_payload


def send(radio, payload):
    
    if radio.write(payload): # Sends and waits ack (2 layer OSI retries included)
        has_payload, pipe_number = radio.available_pipe()
        if has_payload:
            length = radio.getDynamicPayloadSize()
            return (True, radio.read(length))
        else:
            print("Empty ACK")
            return (False, -1)
    else:
        # print("Failed")
        return (False, -1)


def set_global_config(mode):
    global config
    if mode: 
        import configMRM as config
    else:
        import configSR as config


if __name__ == "__main__":
    start_sender(10)
