#!/bin/bash
array=(1 2) # 4 8 16 32 64 128 256 512 1024)
#Simple_ftp_server server-host-name server-port# file-name N MSS
MSS=500

for N in "${array[@]}"
do
        echo $N
        time python3 rdt_client.py ec2-34-207-128-130.compute-1.amazonaws.com 7735 LICENSE $N $MSS
done
