import sys
from mtp_receiver import start_receiver
from mtp_sender import start_sender

def main():
    # Get transmitter or receiver arguments
    mode = -1
    try:
        if(sys.argv[1] == "s"):
            start_sender()
        elif(sys.argv[1] == "r"):
            start_receiver()
        else:
            # Invalid argument
            raise Exception() 
    except:
        print("An argument must be passed. The argument can be: 's' for sender or 'r' for receiver.\nTry calling 'python3 main.py s")
        return

if __name__ == "__main__":
    main()