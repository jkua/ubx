#!/usr/bin/env python3

import logging
import datetime
import time

import serial

from ublox2 import UbloxReader
from ubloxMessage import UbloxMessage

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

    with serial.threaded.ReaderThread(ser, UbloxReader) as protocol:
        try:
            while True:
                msgFormat, msgData = protocol.poll(ser, 'NAV-PVT')
                UbloxMessage.printMessage(msgFormat, msgData, header=datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S.%f]\n'))
                if not args.loop:
                    break
                time.sleep(0.1)

        except KeyboardInterrupt:
            pass
