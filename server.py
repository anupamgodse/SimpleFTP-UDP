import sys
import socket
import random

Rn = 0;

MAX_FRAME_SIZE=1008;
DATA=0
ACK=1
PACKET_TYPES={DATA:'0101010101010101', ACK:'1010101010101010'}

def sendack(connection, addr, seq_no):
    zero=0
    ack = seq_no.to_bytes(4, 'big')+\
            zero.to_bytes(2, 'big')+\
            int(PACKET_TYPES[ACK], 2).to_bytes(2, 'big')

    connection.sendto(ack, addr)

def corrupted(p, frame):
    r = random.uniform(0, 1)
    if(r<=p):
        return True;
    else:
        return False;
    
def disassemble(frame):
    try:
        seq_no = int.from_bytes(frame[:4], 'big')
        data = frame[8:].decode()
        return (seq_no, data)
    except:
        print(frame[:100])
        print("BAD frame")
        exit(0)

if __name__=='__main__':
    port = int(sys.argv[1])
    filename = sys.argv[2]
    p = float(sys.argv[3])
	
    f = open(filename, 'w')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(('', port))

    while(True):
        frame, addr = sock.recvfrom(MAX_FRAME_SIZE)

        if not frame:
            continue
        
        seq_no, data = disassemble(frame)

        if(corrupted(p, frame)):
            print("Packet loss, sequence number = "+str(seq_no))  
            continue;

        if(seq_no == Rn):
            f.write(data)
            Rn += 1;
            sendack(sock, addr, Rn)
