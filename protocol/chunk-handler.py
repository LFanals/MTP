from typing import List
import math
import zlib


def get_file_chunks(filename: str, chunk_size: int) -> List[bytearray]: 
    # Given a filename and the size of the chunks (number of lines) returns a list of the compressed chunks as bytearrays
    print("Creating chunks of size: " + str(chunk_size))
    file = read_file(filename)
    chunks = divide_file(file, chunk_size)
    return compress_chunks(chunks)


def read_file(filename: str) -> str:
    # Opens and reads the specified file with encoding UTF-16. Returns the text of the file as string
    file = open(filename, "r", encoding="UTF-16")
    text = file.read()
    file.close()
    return text

def divide_file(file: str, N: int) -> List[str]:
    # Gets the complete file as a string and divides it by the number of lines specified
    lines = file.split("\n")
    chunks = list()
    print("Number of lines: " + str(len(lines)))

    for j in range(math.ceil(float(len(lines))/N)):
        chunk = ""
        for i in range(N):
            index = j*N + i
            if(index >= len(lines)):
                break
            chunk += lines[index] + "\n"
        chunks.append(chunk)

    print("Number of chunks: " + str(len(chunks)))
    return chunks

def compress_chunks(chunks: List[str]) -> List[bytearray]:
    # Gets all the chunks as strings in a list and compressess each of them.
    compressed_chunks = list()
    for chunk in chunks:
        compressed_chunks.append(compress_chunk(chunk))
    return compressed_chunks


def compress_chunk(chunk: str) -> bytearray:
    # Gets the chunk as a string and compressess it
    chunk_bin = str.encode(chunk)
    return bytearray(zlib.compress(chunk_bin))

def decompress_chunk(compressed: bytearray) -> str:
    chunk = zlib.decompress(bytes(compressed))
    return chunk.decode()

def decompress_chunks(compressed_chunks: List[bytearray]) -> List[str]:
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
    print(chunks[2])

if __name__ == "__main__":
    main()
