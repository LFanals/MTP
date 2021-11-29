from typing import List
import math
import zlib
import utils


def get_file_chunks(filename: str, chunk_size: int, compression_level) -> List[bytearray]: 
    # Given a filename and the size of the chunks (in kB) returns a list of the compressed chunks as bytearrays
    print("Getting file " + filename + " chunks")
    file = read_file(filename)
    chunks = divide_file(file, chunk_size)
    return compress_chunks(chunks, compression_level)


def read_file(filename: str) -> bytes:
    # Opens and reads the specified file with encoding UTF-16. Returns the text of the file as string
    file = open(filename, "rb")
    textBytes = file.read()
    file.close()
    return textBytes

def divide_file(file: bytes, size: int) -> List[bytes]:
    # Gets the complete file in bytes and divides it by the size specified in KB
    size = size * 1000
    chunks = list()
    pointer = 0
    for i in range(math.ceil(float(len(file))/size)):
        chunks.append(file[pointer:(pointer + size)]) 
        pointer = (i+1) * size
    return chunks

def compress_chunks(chunks: List[bytes], compression_level) -> List[bytearray]:
    # Gets all the chunks as strings in a list and compressess each of them.
    compressed_chunks = list()
    for chunk in chunks:
        compressed_chunks.append(compress_chunk(chunk, compression_level))
    return compressed_chunks


def compress_chunk(chunk: bytes, compression_level) -> bytearray:
    # Gets the chunk as bytes and compressess it
    return bytearray(zlib.compress(chunk, level=compression_level))

def decompress_chunk(compressed: bytearray) -> bytes:
    return zlib.decompress(bytes(compressed))

def decompress_chunks(compressed_chunks: List[bytearray]) -> List[bytes]:
    chunks = list()
    for compressed_chunk in compressed_chunks:
           chunks.append(decompress_chunk(compressed_chunk))
    return chunks

def main():
    # For testing purposes
    compressed_chunks = get_file_chunks("large_entire.txt", 10)
    print("Number of compressed chunks: " + str(len(compressed_chunks)))
    chunks = decompress_chunks(compressed_chunks)
    print("Number of decompressed chunks: " + str(len(chunks)))
    print("Size of chunk: " + str(len(chunks[2])))
    file = open("data/test.txt", "wb")
    for chunk in chunks:
        file.write(chunk)
    file.close()


if __name__ == "__main__":
    main()
