from typing import List
import os
import math
import sys

HELLO_PREFIX = 0
CHUNK_INFO_PREFIX = 1
DATA_PREFIX = b'\x02'
SUBCHUNK_SIZE = 31
PAYLOAD_SIZE = 32

CHUNKS_DIR = "./test_compressed_chunks"


def dump(x):
    return ''.join([type(x).__name__, "('",
                    *['\\x'+'{:02x}'.format(i) for i in x], "')"])


def zero_padd_list(list, N):
    if (len(list) != N+1):
        list += (b'\x00') * (N + 1 - len(list))
    return list

def create_hello_frame(chunk_amount):
    print("Creating Hello Frame")
    
    b_chunk_amount = chunk_amount.to_bytes(2, 'little')
    frame = [HELLO_PREFIX, b_chunk_amount[0], b_chunk_amount[1]]
    frame = zero_padd_list(frame, SUBCHUNK_SIZE)
    frame = bytearray(frame)
    return frame


def create_chunk_info_frame(subchunk_amount, chunk_id):
    print("Creating Chunk Info Frame")
    # TODO: Re-implement this function to ensure two bytes for amount
    # It will break if subchunk amount is bigger than 255
    b_subchunk_amount = subchunk_amount.to_bytes(2, 'little')
    frame = [CHUNK_INFO_PREFIX, b_subchunk_amount[0], b_subchunk_amount[1], chunk_id]
    frame = zero_padd_list(frame, SUBCHUNK_SIZE)
    frame = bytearray(frame)
    return frame


def divide_in_subchunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))
    

def create_data_frames(chunk_list):
    print("Creating List of Data Frames")
    
    rts_chunk_list = []

    for i in range(len(chunk_list)):
        # Create subchunks of 31B
        subchunk_list = list(divide_in_subchunks(chunk_list[i], SUBCHUNK_SIZE))
        rts_subchunk_list = []
        for i in range(len(subchunk_list)):
            # Insert "type" prefix at position 0
            subchunk = bytearray(DATA_PREFIX) + subchunk_list[i]

            # 0 padding if necessary
            subchunk = zero_padd_list(subchunk, SUBCHUNK_SIZE)

            # Create list of all the subchunks (in bytes)
            rts_subchunk_list.append(subchunk)

        # Create a list of all the chunks' lists of subchunks
        rts_chunk_list.append(rts_subchunk_list)
    
    return rts_chunk_list



def main():
    chunk_amount = 100

    # generate TEST list with 100 bytearrays
    chunk_list = []
    with open(CHUNKS_DIR+"/chunk1", 'rb') as f:
        byte_list = []
        while True:
            byte = f.read(1)
            if not byte:
                break
            byte_list.append(byte)
    for i in range(chunk_amount):
        chunk_list.append(b''.join(byte_list))
    
    hello_frame = create_hello_frame(chunk_amount)
    print(dump(hello_frame))
    chunk_info_frame = create_chunk_info_frame(106, 3)
    print(dump(chunk_info_frame))
    rts_chunk_list = create_data_frames(chunk_list)
    print("Number of chunks: " + str(len(rts_chunk_list)))
    print("Number of subchunks per chunk: " + str(len(rts_chunk_list[3])))
    print(dump(rts_chunk_list[3][2]))

if __name__ == "__main__":
    main()



    # for filename in os.listdir(CHUNKS_DIR):
    #     chunk_path = os.path.join(CHUNKS_DIR, filename)
    #     chunk_size = os.path.getsize(chunk_path)
    #     subchunk_amount = math.ceil(chunk_size/DATA_PAYLOAD_SIZE)
        
    #     with open(chunk_path, 'rb') as f:
    #         byte_list = []
    #         while True:
    #             byte = f.read(1)
    #             if not byte:
    #                 break
    #             byte_list.append(byte)
            
    #         chunk_list = list(chunks(byte_list, DATA_PAYLOAD_SIZE))
    #         for i in range(len(chunk_list)):
    #             payload = chunk_list[i]
    #             payload.insert(0, DATA_PREFIX)
    #             # print("********************")
                
    #             # 0 padding until 32B
    #             if (len(payload) != DATA_PAYLOAD_SIZE+1):
    #                 print("********************")
    #                 payload += [b'\x00'] * (DATA_PAYLOAD_SIZE + 1 - len(payload))
    #             payload = b''.join(payload)
