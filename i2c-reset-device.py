#!/usr/bin/env python3

from smbus2 import SMBusWrapper
from ubloxI2c import UbloxI2C
import ubloxMessage
from ubloxMessage import UbloxMessage
import logging
import time

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--bus', '-b', type=int, default=11, help='I2C bus number')
    parser.add_argument('--startType', choices=['hot', 'warm', 'cold'], default='cold', help='Specify the start type. This controls what data is cleared. Use the \'clear\' option to specify individual sections to clear.')
    parser.add_argument('--clear', '-c', choices=list(ubloxMessage.navBbrMaskShiftDict.keys()) + ['all', 'none'], nargs='+', default=None, help='Specify the data structures to clear. This overrides \'startType\'.')
    parser.add_argument('--mode', '-m', choices=ubloxMessage.resetModeDict.keys(), default='hw', help='Specify the restart mode.\nsw: Controlled software reset\nswGnssOnly: Controlled software reset (GNSS Only)\nhw: Hardware reset (Watchdog) immediately\nhwShutdown: Hardware reset (Watchdog) after shutdown\ngnssStop: Controlled GNSS stop\ngnssStart: Controlled GNSS start')

    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    #logging.basicConfig(level=logging.DEBUG)

    if args.clear is None:
        if args.startType == 'hot':
            navBbrMask = 0
        elif args.startType == 'warm':
            navBbrMask = 1
        elif args.startType == 'cold':
            navBbrMask = 0xff
    else:
        navBbrMask = UbloxMessage.buildMask(args.clear, UbloxMessage.navBbrMaskShiftDict)

    resetMode = ubloxMessage.resetModeDict[args.mode]

    with SMBusWrapper(args.bus) as bus:
        ublox = UbloxI2C(bus)

        data = ublox.poll('MON-VER', printMessage=True)

        print('\nSending reset...')  
        ublox.sendConfig("CFG-RST", 4, {'nav_bbr': navBbrMask, 'Reset': resetMode})


