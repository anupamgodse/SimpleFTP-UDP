import threading
import sys
import signal
import socket
import time
import copy
import math
from threading import Condition

DATA=0
ACK=1
PACKET_TYPES={DATA:'0101010101010101', ACK:'1010101010101010'}
SERVER_NAME = ''
SERVER_IP = ''
SERVER_PORT = 0
FILENAME = ''
WINDOW_SIZE = 0
MSS = 1400
not_sent_all = True

SEQ_NO = 0
LOCK_SEQ_NO = threading.Lock()
FRAME_STORE = []
LOCK_FRAME_STORE = threading.Lock()

RTO = 0.1
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);

timer = signal.ITIMER_REAL


data = None
data_size = None
rdt_sent_upto = 0
done = False

last_ack = None



class Header:
    def __init__(self, seq_no, checksum, packet_type):
        self.seq_no = seq_no
        self.checksum = checksum
        self.packet_type = packet_type

    def getheader(self):
        return (self.seq_no).to_bytes(4, 'big')+\
                (self.checksum).to_bytes(2, 'big')+\
                int(PACKET_TYPES[self.packet_type], 2).to_bytes(2, 'big')


class Frame:
    def __init__(self, header, data):
        self.header = header
        self.data = data

    def getframe(self):
        return self.header.getheader()+self.data#.encode()

    def getseqno(self):
        return self.header.seq_no


def corrupted(ack):
    return False;

def recv_acks():
    global sock
    global FRAME_STORE
    global SEQ_NO
    global not_sent_all
    global last_ack
    while(not_sent_all):
        ack, server_addr = sock.recvfrom(4096)
        if not ack or corrupted(ack):#ToDO
            continue

        ack_no = int.from_bytes(ack[:4], 'big');
        if(ack_no == last_ack):
            not_sent_all = False
            
        LOCK_FRAME_STORE.acquire()
        LOCK_SEQ_NO.acquire()
        store_size = len(FRAME_STORE);
        if(ack_no > SEQ_NO-store_size  and ack_no <= SEQ_NO):
            for i in range(store_size-(SEQ_NO-ack_no)):
                x = FRAME_STORE.pop(0)
            signal.setitimer(timer, 0)
        LOCK_SEQ_NO.release()
        LOCK_FRAME_STORE.release()


def getchecksum(data):
    checksum = 0
    len_data = len(data)
    if (len_data%2) != 0:
        data += bytearray([0])
        len_data += 1
    
    for byte in range(0, len_data, 2):
        checksum += (data[byte] << 8) + (data[byte + 1])

    checksum = (checksum & 0xFFFF) + (checksum >> 16)
    checksum = ~checksum&0xFFFF
    return checksum


def storeframe(frame):
    global SEQ_NO
    while(True):
        LOCK_FRAME_STORE.acquire()
        if(len(FRAME_STORE) >= WINDOW_SIZE):
            LOCK_FRAME_STORE.release()
            time.sleep(0.05);
        else:
            LOCK_FRAME_STORE.release()
            break;
    LOCK_FRAME_STORE.acquire()
    LOCK_SEQ_NO.acquire()
    FRAME_STORE.append(frame)
    SEQ_NO += 1
    LOCK_SEQ_NO.release()
    LOCK_FRAME_STORE.release()

def sendframe(frame):
    global sock
    global SERVER_IP
    global SERVER_PORT
    frame_data = frame.getframe()
    sock.sendto(frame_data, (SERVER_IP, SERVER_PORT))

def timeout(signum, x):
    global sock
    LOCK_FRAME_STORE.acquire()
    print("Timeout, sequence number = "+str(FRAME_STORE[0].header.seq_no))
    LOCK_FRAME_STORE.release()
    signal.setitimer(timer, RTO);

    LOCK_FRAME_STORE.acquire()
    for each in FRAME_STORE:
        each_copy = copy.copy(each)
        sendframe(each_copy)
    LOCK_FRAME_STORE.release()


def rdt_send():
    global data
    global data_size
    global rdt_sent_upto
    global done
    if(rdt_sent_upto == data_size):
        done = True
        return '\0'
    else:
        currByte=data[rdt_sent_upto]
        rdt_sent_upto+=1
        return currByte


if __name__ == '__main__':
    #global SERVER_NAME
    #global SERVER_PORT
    #global FILENAME
    #global WINDOW_SIZE
    #global MSS
    #global SERVER_IP


    SEVER_NAME = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
    FILENAME = sys.argv[3]
    WINDOW_SIZE = int(sys.argv[4])
    MSS = int(sys.argv[5])

    SERVER_IP = socket.gethostbyname(SEVER_NAME)
    #SERVER_IP = '152.46.17.131'

    signal.signal(signal.SIGALRM, timeout)

    r = threading.Thread(target=recv_acks)
    r.start()

    f = open(FILENAME, 'rb')

    data = f.read()    
    data_size = len(data)

    last_ack = math.ceil(data_size/MSS)

    frame_data = bytearray();

    while(True):
        byte = rdt_send();
        if((done and len(frame_data) > 0) or len(frame_data)==MSS):
            checksum = getchecksum(copy.copy(frame_data))
            header = Header(SEQ_NO, checksum, DATA);
            frame = Frame(header, frame_data)
            storeframe(frame)
            sendframe(frame)

            if(signal.getitimer(timer)[0] == 0):
                signal.setitimer(timer, RTO)

            frame_data = bytearray()
        if not done:
            frame_data += bytearray([byte])
            continue;
        if(done):
            break;

    while not_sent_all:
        if(signal.getitimer(timer)[0] == 0):
            signal.setitimer(timer, RTO)

    r.join()
