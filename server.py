import sys
import socket
import random
import copy

Rn = 0;

MAX_FRAME_SIZE=65000;
DATA=0
ACK=1
PACKET_TYPES={DATA:'0101010101010101', ACK:'1010101010101010'}

def sendack(connection, addr, seq_no):
    zero=0
    ack = seq_no.to_bytes(4, 'big')+\
            zero.to_bytes(2, 'big')+\
            int(PACKET_TYPES[ACK], 2).to_bytes(2, 'big')

    connection.sendto(ack, addr)

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

def notcurrupted(data, checksum):
    return checksum == getchecksum(data)

def corrupted(p, data, checksum):
    r = random.uniform(0, 1)
    if(r<=p or not notcurrupted(data, checksum)):
        return True;
    else:
        return False;
    
def disassemble(frame):
    try:
        checksum = int.from_bytes(frame[4:6], 'big')
        seq_no = int.from_bytes(frame[:4], 'big')
        data = frame[8:]#.decode()
        return (seq_no, data, checksum)
    except:
        print(frame[:100])
        print("BAD frame")
        exit(0)

if __name__=='__main__':
    port = int(sys.argv[1])
    filename = sys.argv[2]
    p = float(sys.argv[3])
	
    f = open(filename, 'wb')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(('localhost', port))

    while(True):
        frame, addr = sock.recvfrom(MAX_FRAME_SIZE)

        if not frame:
            continue
        
        seq_no, data, checksum = disassemble(frame)

        if(corrupted(p, copy.copy(data), checksum)):
            print("Packet loss, sequence number = "+str(seq_no))  
            continue;

        if(seq_no == Rn):
            f.write(data)
            Rn += 1;
            sendack(sock, addr, Rn)
