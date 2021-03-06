# General imports
import subprocess
import time
from datetime import datetime
import os
import sys

# Local files imports
import chunk_handler
import utils
import ioparent

# nrf24 library import
import RF24


filename = os.path.join(utils.WORKING_DIR, "received.txt")

def start_receiver():
    print("Starting receiver")
    set_global_config()
    # Setup nrf24
    radio = setup_receiver()

    # Clean working directory
    clean_working_dir()

    # Wait for Hello frame
    num_chunks = wait_hello(radio)
    
    blink_led = True
    for chunk_id in range(num_chunks):
        # check if master switch is still ON
        #if not ioparent.is_master_on():
        #   return 1

        chunk_is_good = False
        print("\n________________________________")
        print("Receiving chunk ", chunk_id)
        while not chunk_is_good:
            ioparent.update_led_percentage(chunk_id, num_chunks)
            chunk_data = bytearray() 
            # Wait for chunk_info
            num_subchunks = wait_chunk_info(radio, chunk_id)
            
            for subchunk_id in range(num_subchunks):
                data = wait_data_frame(radio, subchunk_id)
                
                if subchunk_id != 0 and subchunk_id % 50 == 0:
                    print("  + Received until subchunk " + str(subchunk_id))
                    ioparent.control_led(1, blink_led)
                    blink_led = not blink_led

                chunk_data.extend(data)
            
            chunk_is_good, decompressed_chunk = try_decompress_chunk(chunk_data)
            wait_chunk_is_good_frame(radio, chunk_is_good, chunk_id)
            if not chunk_is_good:
                print("Chunk was not good expecting to receive again chunk id: " + str(chunk_id))
            
        write_chunk_to_file(filename, decompressed_chunk)        

    radio.stopListening()
    radio.powerDown()
    print("All data has been received correctly, copying file to usb")
    ioparent.control_led(1, False)
    return 0


def setup_receiver():
    print("Setting up the NRF24 configuration")

    radio = RF24.RF24(config.SPI_SPEED)
    radio.begin(utils.CE_PIN, utils.IRQ_PIN) #Set CE and IRQ pins
    radio.setPALevel(config.PA_LEVEL)
    radio.setDataRate(config.DATA_RATE)
    radio.setChannel(config.CHANNEL)
    radio.setRetries(config.RETRY_DELAY,config.RETRY_COUNT)

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
        if not frame_correct:
            print("Wrong hello frame, waiting again")

    num_chunks = int.from_bytes([payload[1], payload[2]], "little")
    print("Hello frame received -> num of chunks: " + str(num_chunks))
    return num_chunks


def wait_chunk_info(radio, expected_chunk_id): 

    # Set a positive payload for the next ack
    frame_correct = False
    count = 0
    while not frame_correct:
        if count != 0: 
            set_next_ack(radio, False, expected_chunk_id) # This will make sender align with us
        else:
            set_next_ack(radio, True, expected_chunk_id)
        payload = wait_data(radio)

        frame_correct = check_chunk_info_frame(payload, expected_chunk_id)
        if not frame_correct:
            print("Wrong chunk_info, waiting again")
        count = count + 1
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
            print("Wrong data frame, waiting again")

    return payload[1:32]


def wait_chunk_is_good_frame(radio: RF24, chunk_is_good, expected_chunk_id):

    frame_correct = False
    while not frame_correct:
        set_next_ack(radio, chunk_is_good, expected_chunk_id)
        payload = wait_data(radio)

        frame_correct = check_chunk_is_good_frame(payload, expected_chunk_id)
        if not frame_correct: 
            print("Wrong chunk_is_good, waiting again")

    print("Chunk is good received -> Chunk id: " + str(expected_chunk_id))
    

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
    return check_frame_type(payload[0], utils.HELLO_TYPE)


def check_chunk_info_frame(payload, expected_id):
    good_type = check_frame_type(payload[0], utils.CHUNK_INFO_TYPE)
    return good_type and check_id(payload[3], expected_id)


def check_data_frame(payload, expected_id):
    (type, id) = get_data_frame_type_and_id(payload)
    good_type = check_frame_type(type, utils.DATA_TYPE)
    return good_type and check_id(id, expected_id)


def check_chunk_is_good_frame(payload, expected_id):
    good_type = check_frame_type(payload[0], utils.CHUNK_IS_GOOD_TYPE)
    chunk_id = int.from_bytes([payload[1], payload[2]], "little")
    return good_type and check_id(chunk_id, expected_id)


def get_data_frame_type_and_id(payload):

    type = payload[0] >> 4 # The 4 left bits
    id = payload[0] & 15 # The 4 right bits
    return (type, id)


def check_id(id, expected_id):
    if id != expected_id:
        print("Wrong id: expected=" + str(expected_id) + ", received=" + str(id))
        return False
    return True


def check_frame_type(type, expected_type):
    if type != expected_type:
        print("Wrong type: expected=" + str(expected_type) + ", received=" + str(type))
        return False
    return True


def set_next_ack(radio: RF24, positive, chunk_id = 0):
    positive_b = 1 if positive else 0 
    radio.writeAckPayload(1, bytearray([positive_b, chunk_id]))


def clean_working_dir():
    if not os.path.exists(utils.WORKING_DIR):
        os.system("mkdir " + utils.WORKING_DIR)
    try:
        os.remove(filename)
    except:
        # Directory already clean
        return


def try_decompress_chunk(chunk_data):
    try:
        decompressed_chunk = chunk_handler.decompress_chunk(chunk_data)
        print("\nDecompression succeed!!")
        return True, decompressed_chunk
    except:
        print("Decompression failed!!")
        return False, -1


def write_chunk_to_file(filename, chunk):
    if not os.path.exists(utils.WORKING_DIR):
        os.system("mkdir " + utils.WORKING_DIR)
    f = open(filename, "ab+")
    f.write(chunk)
    f.close()
    print("Wrote chunk to working directory")


def set_global_config():
    global config
    import configMRM as config


if __name__ == "__main__":
    start_receiver()
    
