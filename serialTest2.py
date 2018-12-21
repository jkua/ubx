#!/usr/bin/env python3

from ublox2 import UbloxReader
from ubloxMessage import UbloxMessage
import serial
import serial.threaded
import time
import datetime
import logging

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', '-d', default='/dev/ttyHS1', help='Specify the serial port device to communicate with. e.g. /dev/ttyO5')
    parser.add_argument('--loop', '-l', action='store_true', help='Keep sending requests in a loop')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    ser = serial.Serial(args.device, 115200, timeout=1)

    with serial.threaded.ReaderThread(ser, UbloxReader) as ublox:
        ublox.printMessageFlag = True
        
        msgFormat, msgData = ublox.poll(ser, 'CFG-PRT')
        UbloxMessage.printMessage(msgFormat, msgData)

        ublox.sendConfig(ser, msgFormat, 20, msgData)

        ublox.saveStreamFlag = True
        while 1:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break


