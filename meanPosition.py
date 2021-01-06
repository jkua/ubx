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
        self.positionBuffer = []
        self.meanUtm = None
        self.converter = CoordinateConverter()

    def userHandler(self, msgTime, msgFormat, msgData, rawMessage):
        if msgFormat == 'NAV-PVT':
            lat = msgData[0]['LAT'] / 1e7
            lon = msgData[0]['LON'] / 1e7
            utmX, utmY, zone = self.converter.convertLLToUtm(lat, lon)
            self.positionBuffer.append((utmX, utmY))

            output = ''
            if msgTime is not None:
                output += '[{}] '.format(datetime.datetime.fromtimestamp(msgTime).strftime('%Y-%m-%d %H:%M:%S.%f'))
            output += f'{lat:.7f}, {lon:.7f} | UTM X: {utmX:.3f}, Y: {utmY:.3f}, Zone: {zone}'
            print(output)

    def getMeanUtm(self):
        utmData = np.array(self.positionBuffer)
        self.meanUtm = utmData.mean(axis=0)
        self.stdUtm = utmData.std(axis=0)
        return self.meanUtm

    def getMeanLatLon(self):
        if self.meanUtm is None:
            self.getMeanUtm()
        return self.converter.convertUtmToLL(self.meanUtm[0], self.meanUtm[1])


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

    ser = serial.Serial(args.device, 1000000, timeout=0.1)

    with serial.threaded.ReaderThread(ser, Reader) as reader:
        while True:
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                break

        lat, lon = reader.getMeanLatLon()
        print(f'\n# measurements: {len(reader.positionBuffer)} | Mean lat/lon: {lat:.9f}, {lon:.9f} | UTM X/Y: {reader.meanUtm[0]:.3f}, {reader.meanUtm[1]:.3f}, Zone: {reader.converter.zone} | Std X: {reader.stdUtm[0]:.3f} m, Y: {reader.stdUtm[1]:.3f} m')
