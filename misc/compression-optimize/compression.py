from typing import Tuple
import zlib
from texttable import Texttable
import glob, os

# files = ["large.txt", "short.txt"]
files = []

def main():
    # Get files
    # os.chdir('files/')
    Files = glob.glob("files/*.txt")
    Filess = []
    Names = []
    for file in Files:
        if (file != 'files\\large.txt'):
            file = file.replace("files\\", "")
            file = file.replace(".txt", "")
            Names.append(int(file))
            Filess.append(file)

    # Sort files
    NamesFiles = list(zip(Names, Filess))
    NamesFiles.sort()
    FilesSorted = [Filess for Names, Filess in NamesFiles]

    for file in FilesSorted:
        files.append("files\\"+file+".txt")

    # print(files)


    # Operate with files
    results = []
    results.append(["Scheme", "Original (kB)", "Compressed (kB)", "rate", "1/Original (kB)", "rate*1/Original (kB)"])

    for file in files:
        # Open file
        name = file.replace(".txt", "")
        text = readFile(file)
        original_size = len(text.encode("UTF-16"))/1000

        # Compress file entirely
        size, compressed = compress_entire_file(text)
        size = size / 1000

        # Decompress 
        text = decompress([compressed])

        # Write output
        writeFile('entires/'+name+"_entire.txt", text)
        
        results.append([name+"_entire", original_size, size, 1 - size/original_size, 1/original_size, (1 - size/original_size)*1/original_size])

    # Show results
    show_results(results)

def readFile(filename: str) -> str:
    # Open file
    file = open(filename, "r", encoding="UTF-16")
    text = file.read()
    file.close()
    return text

def writeFile(filename: str, text):
    outFile = open(filename, "w", encoding="UTF-16")
    outFile.write(text)
    outFile.close()

def compress_entire_file(file_text: str) -> Tuple[int, bytes]:
    # Compress entire file
    binaryFile = str.encode(file_text)
    compressed = zlib.compress(binaryFile)
    return len(compressed), compressed

def compress_by_line(file_text: str) -> Tuple[int, list]:
    # Compress by line
    lines = file_text.split("\n")
    compressed_lines = []
    count = 0
    size = 0
    for line in lines:
        line_bin = str.encode(line)
        compressed_line =  bytearray(zlib.compress(line_bin))
        compressed_lines.append(compressed_line)
        count += 1
        size += len(compressed_line)
    return size, compressed_lines

def decompress(compressed: list) -> str:
    # Decompress by line 
    l = ""
    for cl in compressed:
        l += zlib.decompress(cl).decode() + "\n"
    return l

def show_results(results: list):
    # assume that your data rows are tuples
    t = Texttable()
    t.add_rows(results)
    print(t.draw())


if __name__ == "__main__":
    main()
