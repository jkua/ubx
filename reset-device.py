#!/usr/bin/env python3

import logging
import datetime
import time

import serial

from ublox2 import UbloxReader
from ubloxMessage import UbloxMessage, navBbrMaskShiftDict, resetModeDict

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--startType', choices=['hot', 'warm', 'cold'], default='cold', help='Specify the start type. This controls what data is cleared. Use the \'clear\' option to specify individual sections to clear.')
    parser.add_argument('--clear', '-c', choices=list(navBbrMaskShiftDict.keys()) + ['all', 'none'], nargs='+', default=None, help='Specify the data structures to clear. This overrides \'startType\'.')
    parser.add_argument('--mode', '-m', choices=resetModeDict.keys(), default='hw', help='Specify the restart mode.\nsw: Controlled software reset\nswGnssOnly: Controlled software reset (GNSS Only)\nhw: Hardware reset (Watchdog) immediately\nhwShutdown: Hardware reset (Watchdog) after shutdown\ngnssStop: Controlled GNSS stop\ngnssStart: Controlled GNSS start')
    parser.add_argument('--device', '-d', help='Specify the serial port device to communicate with. e.g. /dev/ttyO5')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    if args.clear is None:
        if args.startType == 'hot':
            navBbrMask = 0
        elif args.startType == 'warm':
            navBbrMask = 1
        elif args.startType == 'cold':
            navBbrMask = 0xff
    else:
        navBbrMask = UbloxMessage.buildMask(args.clear, UbloxMessage.navBbrMaskShiftDict)

    resetMode = resetModeDict[args.mode]

    ser = serial.Serial(args.device, 115200, timeout=1)

    with serial.threaded.ReaderThread(ser, UbloxReader) as protocol:
        msgFormat, msgData = protocol.poll(ser, 'MON-VER')
        UbloxMessage.printMessage(msgFormat, msgData, header=datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S.%f]\n'))

        print('\nSending reset...')  
        protocol.sendMessage(ser, "CFG-RST", 4, {'nav_bbr': navBbrMask, 'Reset': resetMode})
