#!/usr/bin/env python3

import logging
import datetime
import time

import serial
import numpy as np

from ublox2 import UbloxReader
from ubloxMessage import UbloxMessage
from coordinateConverter import CoordinateConverter


class Reader(UbloxReader):
    def __init__(self):
        super().__init__()
        self.home = None
        self.converter = CoordinateConverter()

    def setHome(self, lat, lon):
        self.home = self.converter.convertLLToUtm(lat, lon)

    def userHandler(self, msgTime, msgFormat, msgData, rawMessage):
        if msgFormat == 'HNR-PVT':
            # try:
                lat = msgData[0]['LAT'] / 1e7
                lon = msgData[0]['LON'] / 1e7
                utmX, utmY, zone = self.converter.convertLLToUtm(lat, lon)
                dx = utmX - self.home[0]
                dy = utmY - self.home[1]
                distance = np.linalg.norm([dx, dy])

                output = ''
                if msgTime is not None:
                    output += '[{}] '.format(datetime.datetime.fromtimestamp(msgTime).strftime('%Y-%m-%d %H:%M:%S.%f'))
                output += f'Distance: {distance:.3f} m | dx: {dx:.3f}, dy: {dy:.3f}'
                print(output)
            # except:
            #     print('*** Failed to parse message!')


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('lat', type=float, help='Home latitude')
    parser.add_argument('lon', type=float, help='Home longitude')
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

    ser = serial.Serial(args.device, 1000000, timeout=0.1)

    with serial.threaded.ReaderThread(ser, Reader) as reader:
        reader.setHome(args.lat, args.lon)
        while True:
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                break
