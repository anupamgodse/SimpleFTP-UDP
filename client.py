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
SERVER_PORT = 0
FILENAME = ''
WINDOW_SIZE = 0
MSS = 1400

SEQ_NO = 0
LOCK_SEQ_NO = threading.Lock()
FRAME_STORE = []
LOCK_FRAME_STORE = threading.Lock()

RTO = 0.5
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

timer = signal.ITIMER_REAL

class Header:
    def __init__(self, seq_no, checksum, packet_type):
        self.seq_no = seq_no
        self.checksum = checksum
        self.packet_type = packet_type

    def getheader(self):
        return '{:032b}'.format(self.seq_no)+\
                '{:016b}'.format(self.checksum)+\
                PACKET_TYPES[self.packet_type]


class Frame:
    def __init__(self, header, data):
        self.header = header
        self.data = data

    def getframe(self):
        return self.header.getheader()+self.data

    def getseqno(self):
        return self.header.seq_no


def corrupted(ack):
    return False;

def recv_acks():
    #print("I am receiver")
    global sock
    global FRAME_STORE
    global SEQ_NO
    #while(True):
    ack = sock.recv(4096).decode()
    if not ack or corrupted(ack):#ToDO
        return;

    ack_no = int(ack[:32], 2)
    #print("ack_no= "+str(ack_no))

    #print("recv_acks: acquiring lock frame")
    LOCK_FRAME_STORE.acquire()
    #print("recv_acks: acquired lock frame")
    #print("recv_acks: acquiring lock SEQ")
    LOCK_SEQ_NO.acquire()
    #print("recv_acks: acquired lock SEQ")
    store_size = len(FRAME_STORE);
    if(ack_no > SEQ_NO-store_size  and ack_no <= SEQ_NO):
        for i in range(store_size-(SEQ_NO-ack_no)):
            x = FRAME_STORE.pop(0)
            #print("scraped = "+str(x.header.seq_no))
        signal.setitimer(timer, 0)
    LOCK_SEQ_NO.release()
    LOCK_FRAME_STORE.release()
    #print("recv_acks: released locks")


def getchecksum(data):
    return 100;


def storeframe(frame):
    global SEQ_NO
    while(True):
        #print("storeframe: acquiring lock frame")
        LOCK_FRAME_STORE.acquire()
        #print("storeframe: acquired lock frame")
        if(len(FRAME_STORE) >= WINDOW_SIZE):
            LOCK_FRAME_STORE.release()
            #print("storeframe: released locks")
            time.sleep(1);
        else:
            LOCK_FRAME_STORE.release()
            #print("storeframe: released locks")
            break;
    #print("storeframe: acquiring lock frame")
    LOCK_FRAME_STORE.acquire()
    #print("storeframe: acquired lock frame")
    #print("storeframe: acquiring lock SEQ")
    LOCK_SEQ_NO.acquire()
    #print("storeframe: acquired lock SEQ")
    FRAME_STORE.append(frame)
    SEQ_NO += 1
    LOCK_SEQ_NO.release()
    #print("storeframe: releasing lock frame")
    LOCK_FRAME_STORE.release()
    #print("storeframe: released lock frame")

def sendframe(sock, frame):
    #print("In Send Frame seqNO = "+str(frame.header.seq_no))
    #print(frame.header.checksum)
    #print(frame.header.packet_type)
    #print(frame.data)
    frame_data = frame.getframe()
    sock.sendall(frame_data.encode())

def timeout(signum, x):
    print("timeout")
    global sock
    signal.setitimer(timer, RTO);

    LOCK_FRAME_STORE.acquire()
    for each in FRAME_STORE:
        each_copy = copy.copy(each)
        sendframe(sock, each_copy)
    LOCK_FRAME_STORE.release()

if __name__ == '__main__':
    SEVER_NAME = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
    FILENAME = sys.argv[3]
    WINDOW_SIZE = int(sys.argv[4])
    MSS = int(sys.argv[5])

    server_ip = socket.gethostbyname(SEVER_NAME)

    sock.connect((server_ip, SERVER_PORT))

    signal.signal(signal.SIGALRM, timeout)

    #r = threading.Thread(target=recv_acks)
    #r.start()

    f = open(FILENAME, 'r')

    data = f.read()    
    data_size = len(data)

    total = (int(data_size/MSS)) + 1
    print("MSS= "+ str(MSS), total)

    while(SEQ_NO < total):
        if(SEQ_NO == total-1):
            #print("entireleft")
            frame_data = data[SEQ_NO*MSS:]
        else:
            #print("just MSS")
            frame_data = data[SEQ_NO*MSS:(SEQ_NO+1)*MSS]

        checksum = getchecksum(frame_data)
        header = Header(SEQ_NO, checksum, DATA);
        frame = Frame(header, frame_data)
        storeframe(frame)
        #print(frame.header.seq_no, frame.header.checksum, frame.data)
        sendframe(sock, frame)


        #print("curretn= "+str(signal.getitimer(timer)))
        if(signal.getitimer(timer)[0] == 0):
            #print("timer")
            signal.setitimer(timer, RTO)

        recv_acks()



    #r.join()

    print("Done")
