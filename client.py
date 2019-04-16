import threading
import sys

DATA=0
ACK=1
PACKET_TYPES={DATA:'0101010101010101', ACK:'1010101010101010'}

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


#class Window:
#    def __init__(self, size):
#        self.size = size
#        self.sn = 0;
#        self.sf = 0;
#        self.filled=0;
#        self.frames = []
#        for each in range(size):
#            self.frames.append(Frame())
        
if __name__ == '__main__':
    #w = Window(4)
    
    server_name = sys.argv[1]
    server_port = int(sys.argv[2])
    filename = sys.argv[3]
    window_size = int(sys.argv[4])
    MSS = int(sys.argv[5])

    sn = 0;
    sf = 0;

    r = threading.Thread(target=receiver)

    f = open(filename, 'r')

    data = f.read()    
    data_size = len(data)

    while(data_size > 0):
        while(sn-sf>=window_size):


    

    r.start()

    r.join()

    print("Done")
