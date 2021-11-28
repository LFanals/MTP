# General imports
import subprocess
import time
from datetime import datetime
import os
import sys

# Local files imports
import chunk_handler
import utils

# nrf24 library import
import RF24


filename = os.path.join(utils.WORKING_DIR, "received.txt")

def start_receiver():
    print("Starting receiver")

    # Setup nrf24
    radio = setup_receiver()

    # Clean working directory
    clean_working_dir()

    # Wait for Hello frame
    num_chunks = wait_hello(radio)
    
    # At this point a positive ack has been sent
    #ioparent.control_led(1, True)
    #ioparent.control_led(3, True)

    for i in range(num_chunks):
        
        # LEDs 3, 4 and 5 will indicate the received percentage
        #if i > 2*num_chunks/3: 
        #    ioparent.control_led(4, True)
        #elif i >= num_chunks - 1:
        #    ioparent.control_led(5, True)


        chunk_data = bytearray()
        # Wait for chunk_info
        num_subchunks = wait_chunk_info(radio, i)
        
        
        for subchunk_id in range(num_subchunks):
            data = wait_data_frame(radio, subchunk_id)
            
            if subchunk_id != 0 and subchunk_id%25 == 0:
                print("Received until subchunk " + str(subchunk_id))
            
            # Add the data to the chunk data bytearray
            chunk_data.extend(data)
        
        success, decompressed_data = try_decompress_chunk(chunk_data)
        wait_chunk_is_good_frame(radio, success, i)
        if not success:
            print("Chunk was not good expecting to receive again chunk id: " + str(i))
            i = i - 1
        #write_chunk_to_file(filename, decompressed_chunk)        

    radio.stopListening()
    radio.powerDown()
    print("All data has been received correctly, copying file to usb")
    #ioparent.control_led(0, False)
    #subprocess.call("./write_usb.sh")


def setup_receiver():
    print("Setting up the NRF24 configuration")

    radio = RF24.RF24(utils.SPI_SPEED)
    radio.begin(utils.CE_PIN, utils.IRQ_PIN) #Set CE and IRQ pins
    radio.setPALevel(utils.PA_LEVEL)
    radio.setDataRate(utils.DATA_RATE)
    radio.setChannel(utils.CHANNEL)
    radio.setRetries(utils.RETRY_DELAY,utils.RETRY_COUNT)

    radio.enableDynamicPayloads()  
    radio.enableAckPayload()

    radio.openWritingPipe(utils.RX_WRITE_PIPE)
    radio.openReadingPipe(1, utils.TX_WRITE_PIPE)

    radio.powerUp()
    radio.printPrettyDetails()

    radio.startListening()
    return radio


def wait_hello(radio):

    frame_correct = False
    while not frame_correct:
        set_next_ack(radio, True)
        payload = wait_data(radio)
    
        frame_correct = check_hello_frame(payload)

    num_chunks = int.from_bytes([payload[1], payload[2]], "little")
    print("Hello frame received -> num of chunks: " + str(num_chunks))
    return num_chunks


def wait_chunk_info(radio, expected_chunk_id): 

    # Set a positive payload for the next ack
    frame_correct = False
    while not frame_correct:
        set_next_ack(radio, True)
        payload = wait_data(radio)

        frame_correct = check_chunk_info_frame(payload, expected_chunk_id)

    (num_subchunks, chunk_id) = get_chunk_info_data(payload)
    print("Chunk_info received -> Chunk id: " + str(chunk_id) + ", num of subchunks: " + str(num_subchunks))
    
    return num_subchunks


def wait_data_frame(radio: RF24, expected_id):
    expected_id = expected_id % 15

    frame_correct = False
    while not frame_correct:
        set_next_ack(radio, True)
        payload = wait_data(radio)

        frame_correct = check_data_frame(payload, expected_id)
        if not frame_correct: 
            print("frame incorrect, waiting again")

    return payload[1:32]

def wait_chunk_is_good_frame(radio: RF24, success, chunk_id):

    frame_correct = False
    while not frame_correct:
        set_next_ack(radio, success)
        payload = wait_data(radio)

        frame_correct = check_chunk_is_good_frame(payload, chunk_id)
        if not frame_correct: 
            print("frame incorrect, waiting again")

    print("Chunk is good received -> Chunk id: " + str(chunk_id))
    

def set_next_ack(radio: RF24, positive):
    positive_b = 1 if positive else 0 
    radio.writeAckPayload(1, bytearray([positive_b]))


def wait_data(radio: RF24):
    has_data, pipe_number = radio.available_pipe()
    # TODO: Implement timeout to wait
    while not has_data:
        has_data, pipe_number = radio.available_pipe()
        time.sleep(0.000001)

    length = radio.getDynamicPayloadSize()
    return radio.read(length)


def get_chunk_info_data(payload):
    subchunks_num = int.from_bytes([payload[1], payload[2]], "little")
    chunk_id = payload[3] 
    return (subchunks_num, chunk_id)

def get_data_frame_data(payload):
    return payload[1:32]


def check_hello_frame(payload):
    return check_frame_type(payload, utils.HELLO_TYPE)


def check_chunk_info_frame(payload, expected_id):
    good_type = check_frame_type(payload, utils.CHUNK_INFO_TYPE)
    return good_type and payload[3] == expected_id


def check_data_frame(payload, expected_id):
    (type, id) = get_data_frame_type_and_id(payload)
    good_type = type == utils.DATA_TYPE
    return good_type and id == expected_id


def check_chunk_is_good_frame(payload, expected_id):
    good_type = check_frame_type(payload, utils.CHUNK_IS_GOOD_TYPE)
    chunk_id = int.from_bytes([payload[1], payload[2]], "little")
    return good_type and chunk_id == expected_id 

def get_data_frame_type_and_id(payload):

    type = payload[0] >> 4 # The 4 left bits
    id = payload[0] & 15 # The 4 right bits

    return (type, id)


def check_frame_type(payload, type):
    if payload[0] != type:
        print("Frame received is not correct type: expected=" + str(type) + ", received=" + str(payload[0]))
        return False
    return True

def clean_working_dir():
    try:
        os.remove(filename)
    except:
        # Directory already clean
        return


def try_decompress_chunk(chunk_data):
    try:
        decompressed_chunk = chunk_handler.decompress_chunk(chunk_data)
        return True, decompressed_chunk
    except:
        return False, -1

def write_chunk_to_file(filename, chunk):
    f = open(filename, "ab")
    f.write(chunk)
    f.close()


if __name__ == "__main__":
    start_receiver()