from typing import Tuple
import zlib
from texttable import Texttable

file = 'large.txt'
N = [1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8000]

def main():
    # Open file
    name = file.replace(".txt", "")
    text = readFile(file)
    lines = text.splitlines()
    acum = ''
    i = 1
    for line in lines:
        acum += line
        if (i in N):
            # Write output
            writeFile(str(i)+".txt", acum)
        i += 1


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


if __name__ == "__main__":
    main()
