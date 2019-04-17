import sys
import socket
import random

Rn = 0;

MAX_FRAME_SIZE=4096;
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
    if(r<=p):
        return True;
    else:
        return False;
    
def disassemble(frame):
    seq_no = int(frame[:32], 2)
    #print(seq_no)
    data = frame[64:]
    return (seq_no, data)



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
        frame = connection.recv(MAX_FRAME_SIZE).decode()
        #print(frame)

        if not frame:
            continue
        
        seq_no, data = disassemble(frame)
        print(seq_no)
        print(data)

        #print(seq_no, data)

        if(corrupted(p, frame)):
            print("Packet loss, sequence number = "+str(seq_no))  
            continue;

        print(seq_no)
        print(Rn)

        if(seq_no == Rn):
            print("Received "+ str(Rn))
            f.write(data)
            Rn += 1;
            sendack(connection, Rn)

