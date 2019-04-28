import threading
import sys
import signal
import socket
import time
import copy

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

RTO = 0.5
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);

timer = signal.ITIMER_REAL

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
        return self.header.getheader()+self.data.encode()

    def getseqno(self):
        return self.header.seq_no


def corrupted(ack):
    return False;

def recv_acks():
    global sock
    global FRAME_STORE
    global SEQ_NO
    while(True):
        print("Running")
        ack, server_addr = sock.recvfrom(4096)
        if not ack or corrupted(ack):#ToDO
            print("No ack")
            return;

        ack_no = int.from_bytes(ack[:4], 'big');
        print(ack_no)
        #if(ack_no == 37):
        #    not_sent_all = False
        #    exit()
            

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
    return 100;


def storeframe(frame):
    global SEQ_NO
    while(True):
        LOCK_FRAME_STORE.acquire()
        if(len(FRAME_STORE) >= WINDOW_SIZE):
            LOCK_FRAME_STORE.release()
            time.sleep(1);
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
    print("Indsend frame", SERVER_IP, SERVER_PORT)
    frame_data = frame.getframe()
    sock.sendto(frame_data, (SERVER_IP, SERVER_PORT))
    #if(signal.getitimer(timer)[0] == 0):
    #    signal.setitimer(timer, RTO)

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

if __name__ == '__main__':
    SEVER_NAME = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
    FILENAME = sys.argv[3]
    WINDOW_SIZE = int(sys.argv[4])
    MSS = int(sys.argv[5])

    SERVER_IP = socket.gethostbyname(SEVER_NAME)
    print(SERVER_IP)

    signal.signal(signal.SIGALRM, timeout)

    r = threading.Thread(target=recv_acks)
    r.start()

    f = open(FILENAME, 'r')

    data = f.read()    
    data_size = len(data)

    total = (int(data_size/MSS)) + 1
    print(total)

    while(SEQ_NO < total):
        if(SEQ_NO == total-1):
            frame_data = data[SEQ_NO*MSS:]
        else:
            frame_data = data[SEQ_NO*MSS:(SEQ_NO+1)*MSS]

        checksum = getchecksum(frame_data)
        header = Header(SEQ_NO, checksum, DATA);
        frame = Frame(header, frame_data)
        storeframe(frame)
        sendframe(frame)

        print("Sending")

        if(signal.getitimer(timer)[0] == 0):
            signal.setitimer(timer, RTO)

        #recv_acks()
    while True:
        LOCK_FRAME_STORE.acquire()
        if(len(FRAME_STORE) == 0):
                continue;
        LOCK_FRAME_STORE.release()
        if(signal.getitimer(timer)[0] == 0):
            signal.setitimer(timer, RTO)

        x=1
    r.join()
