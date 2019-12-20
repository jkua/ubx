#!/usr/bin/env python3

import datetime
import bitstring
import crcmod
import serial
from ubloxMessage import UbloxMessage

RTCM3_PREAMBLE = 0xD3
UBX_PREAMBLE = b'\xB5\x62'
RTCM3_MESSAGE_TYPES = {1005: 'Stationary RTK reference station ARP',
                      1074: 'GPS MSM4',
                      1077: 'GPS MSM7',
                      1084: 'GLONASS MSM4',
                      1087: 'GLONASS MSM7',
                      1094: 'Galileo MSM4',
                      1097: 'Galileo MSM7',
                      1124: 'BeiDou MSM4',
                      1127: 'BeiDou MSM7',
                      1230: 'GLONASS code-phase biases',
                      4072: 'Reference station information'
                      }

def parseMessage(buf):
    while len(buf) > 1:
        if buf[0] == RTCM3_PREAMBLE:
            try:
                message, buf = parseRtcm3(buf)
                return message, buf
            except:
                raise
        elif buf[:2] == UBX_PREAMBLE:
            try:
                message, buf = parseUbx(buf)
                return message, buf
            except:
                raise
        print('First character(s) [{}] do not match preamble, skipping...'.format(buf[:2]))
        buf = buf[1:]
    return None, buf

# CRC-24Q (Qualcomm) for RTCM parity check
# Mask 0x1864CFB, not reversed, not XOR'd
crc24q = crcmod.mkCrcFun(0x1864CFB, initCrc=0, rev=False, xorOut=0)
        
def parseRtcm3(buf):
    # rtcm3 message format:
    # +----------+--------+-----------+--------------------+----------+
    # | preamble | 000000 |  length   |    data message    |  parity  |
    # +----------+--------+-----------+--------------------+----------+
    # |<-- 8 --->|<- 6 -->|<-- 10 --->|<--- length x 8 --->|<-- 24 -->|

    if buf[0] == RTCM3_PREAMBLE:
        receivedDt = datetime.datetime.now()
        length = (buf[1] << 8) + buf[2]
        if length > 300:
            print('Invalid length! ({})'.format(length))
            buf = buf[:1]
            return None, buf
        elif len(buf) < (length + 6):
            # print('Not enough data! Got {}, need {}'.format(len(buf), length+6))
            return None, buf
        message = buf[:length+3]
        parity = buf[length+3:length+6]

        # Check parity
        crc = crc24q(message)
        crcBytes = crc.to_bytes(3, byteorder='big')
        if crcBytes != parity:
            print('**** PARITY MISMATCH reading RTCM message!')
            buf = buf[1:]
            return None, buf

        # Get payload and message type
        payload = bitstring.BitArray(message[3:])
        messageType = payload[:12].uint
        if messageType == 1074:
            print('')
        print('[{}] RTCM3 {} ({}) | Length: {} ({})'.format(receivedDt.strftime('%H:%M:%S.%f'), messageType, RTCM3_MESSAGE_TYPES[messageType], length, length+6))
        output = {'messageType': 'RTCM3-{}: {}'.format(messageType, RTCM3_MESSAGE_TYPES[messageType]), 'payload': payload, 'fullMessage': message+parity}

        # Remove processed data
        buf = buf[length+6:]
        return output, buf
    else:
        raise ValueError('Preamble mismatch!')

def parseUbx(buf):
    msgFormat, msgData, remainder = UbloxMessage.parse(buf, raw=True)
    print('\nUBX {} | Length: {}'.format(msgFormat, len(msgData)))
    output = {'messageType': 'UBX-{}'.format(msgFormat), 'payload': msgData}
    return output, remainder


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f')
    parser.add_argument('--device', '-d')
    args = parser.parse_args()

    if args.file is not None:
        f = open(args.input, 'rb')
        buf = f.read()

        while len(buf) > 0:
            try:
                message, buf = parseMessage(buf)
            except:
                raise

    elif args.device is not None:
        with serial.Serial(args.device, 9600, timeout=0) as ser:
            buf = b''
            while True:
                buf += ser.read(200)
                try:
                    message, buf = parseMessage(buf)
                except KeyboardInterrupt:
                    break
                except (ValueError, IndexError):
                    pass
