import chunk_creator
import packet_creator
import nrf24

HELLO_PREFIX = 0
CHUNK_INFO_PREFIX = 1
DATA_PREFIX = b'\x02'
SUBCHUNK_SIZE = 31
PAYLOAD_SIZE = 32
CHUNKS_DIR = "./test_compressed_chunks"

def main():
    chunk_size = 100

    # Creating Chunks
    chunk_list = chunk_creator.get_file_chunks("large_entire.txt", chunk_size)
    chunk_amount = len(chunk_list)
    print("Number of compressed chunks: " + str(chunk_amount))
    
    # Creating hello frame
    hello_frame = packet_creator.create_hello_frame(chunk_amount)
    print("    " + packet_creator.dump(hello_frame))

    # Creating chunk_info frame
    chunk_info_frame = packet_creator.create_chunk_info_frame(106, 3)
    print("    " + packet_creator.dump(chunk_info_frame))
    
    # Creating data frames
    rts_chunk_list = packet_creator.create_data_frames(chunk_list)
    print("Number of chunks: " + str(len(rts_chunk_list)))
    print("Number of subchunks per chunk: " + str(len(rts_chunk_list[3])))
    print("    " + packet_creator.dump(rts_chunk_list[3][2]))

if __name__ == "__main__":
    main()

