#!/usr/bin/env python3

import serial
import time
from readRtcm import *

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f')
    parser.add_argument('--device1')
    parser.add_argument('--device2')
    args = parser.parse_args()

    f = open(args.file, 'rb')
    buf = f.read()

    messages = []
    while len(buf) > 0:
        try:
            message, buf = parseMessage(buf)
            if message['messageType'].startswith('RTCM3'):
                messages.append(message)
        except:
            raise

    print('Parsed {} RTCM3 messages'.format(len(messages)))

    with serial.Serial(args.device1, 57600, timeout=0) as ser1,\
         serial.Serial(args.device2, 57600, timeout=0) as ser2:      

        for i, message in enumerate(messages, 1):
            try:
                sent = message['fullMessage']
                print('\nSending messsage {}: {} ({} bytes)'.format(i, message['messageType'], len(sent)))

                ser1.write(sent)
                received = b''
                startTime = time.time()
                while len(received) < len(sent):
                    received += ser2.read(len(message['fullMessage']))
                    elapsedTime = time.time() - startTime
                    if elapsedTime > 1:
                        break

                output = 'Received {} bytes in {:.3f} ms ({:.3f} bits/s)- '.format(len(received), elapsedTime*1000, len(received)*8/elapsedTime)
                if sent == received:
                    output += 'data matches'
                else:
                    output += 'DATA MISMATCH!'

                sent = b''

                print(output)
            except KeyboardInterrupt:
                break

        ser1.close()
        ser2.close()
            