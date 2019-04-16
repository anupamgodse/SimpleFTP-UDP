import threading
import sys

DATA=0
ACK=1
PACKET_TYPES={DATA:'0101010101010101', ACK:'1010101010101010'}
SERVER_NAME = ''
SERVER_PORT = ''
FILENAME = ''
WINDOW_SIZE = 0
MSS = 1400
Sn = 0
Sf = 0
SEQ_NO = 0
FRAME_STORE = []

RTO = 0.5

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
    def set_attr(self, header, data):
        self.header = header
        self.data = data

    def getframe(self):
        return self.header.getheader()+self.data

    def getseqno(self):
        return self.header.seq_no


def recv_acks():
    print("I am receiver")
    global sock
    while(True):
    	ack = sock.recv(4096)
    	if(currupted(ack)):
		continue;
	
	if(ack_no > Sf and ack_no <= Sn):
		for i in range(ack_no-Sf):
			FRAME_STORE.pop(0)
		signal.setitimer(timer, 0)
	


def getchecksum(data):
	return 100;


def storeframe(frame):
	while(len(FRAME_STORE) >= WINDOW_SIZE):
		sleep(1);
	
	FRAME_STORE.append(frame)

def sendframe(sock, frame):
	frame_data = frame.getframe()
	sock.sendall(frame_data)

def timeout(signum, frame):
	signal.setitimer(timer, RTO)
	for each in FRAME_STORE:
		sendframe(sock, frame)
	
        
if __name__ == '__main__':
    #w = Window(4)
    
    SEVER_NAME = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
    FILENAME = sys.argv[3]
    WINDOW_SIZE = int(sys.argv[4])
    MSS = int(sys.argv[5])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    server_ip = gethostbyname(SEVER_NAME)
    
    sock.connect((server_ip, SEVER_PORT))
    
    signal.signal(signal.SIGALRM, timeout)

    r = threading.Thread(target=receiver)

    f = open(filename, 'r')

    data = f.read()    
    data_size = len(data)

    while(data_size > 0):
        #while(sn-sf>=window_size):
	frame_data = SEQ_NO*MSS:(SEQ_NO+1)*MSS]
	checksum = getchecksum(frame_data)
	header = Header(SEQ_NO, checksum, DATA);
	frame = Frame(header, frame_data)
	sendframe(sock, frame)
	SEQ_NO += 1

	if(signal.getitimer(timer) == 0):
		signal.setitimer(timer, RTO)
	
	
	

    

    r.start()

    r.join()

    print("Done")
