import sys
import socket
import random

Rn = 0;

MAX_FRAME_SIZE=1064;
DATA=0
ACK=1
PACKET_TYPES={DATA:'0101010101010101', ACK:'1010101010101010'}

def sendack(connection, seq_no):
    ack = '{:032b}'.format(seq_no)+\
            '{:016b}'.format(0)+\
            PACKET_TYPES[ACK]

    connection.sendall(ack.encode())

def corrupted(p, frame):
    r = random.uniform(0, 1)
    print(r, p)
    if(r<=p):
        return True;
    else:
        return False;
    
def disassemble(frame):
    try:
        seq_no = int(frame[:32], 2)
        #print(seq_no)
        data = frame[64:]
        return (seq_no, data)
    except:
        print(frame[:100])
        print("BAD frame")
        exit(0)

def print_pro(frame):
    print(frame[:32]);
    print(frame[32:48])
    print(frame[48:64])
    print(frame[64:])



if __name__=='__main__':
    port = int(sys.argv[1])
    filename = sys.argv[2]
    p = float(sys.argv[3])
	
    f = open(filename, 'w')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind(('', port))

    sock.listen()

    connection, client_address = sock.accept();
    
    while(True):
        #print("Expected= "+ str(Rn))
        frame = connection.recv(MAX_FRAME_SIZE).decode()
        #print(frame)
        #print_pro(frame)

        if not frame:
            continue
        
        seq_no, data = disassemble(frame)
        print(seq_no)
        #print(data)

        #print(seq_no, data)

        if(corrupted(p, frame)):
            print("Packet loss, sequence number = "+str(seq_no))  
            continue;

        #print(seq_no)
        #print(Rn)

        if(seq_no == Rn):
            #print("Received "+ str(Rn))
            f.write(data)
            Rn += 1;
            sendack(connection, Rn)

