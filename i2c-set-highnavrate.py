#!/usr/bin/env python3

from smbus2 import SMBusWrapper
from ubloxI2c import UbloxI2C
import logging
import time

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('navRate', type=int)
    parser.add_argument('--bus', '-b', type=int, default=11, help='I2C bus number')
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    #logging.basicConfig(level=logging.DEBUG)

    with SMBusWrapper(args.bus) as bus:
        ublox = UbloxI2C(bus)

        print('\nCurrent configuration')
        print('---------------------')
        data = ublox.poll('CFG-HNR', printMessage=True)

        data[0]['HighNavRate'] = args.navRate
        
        ublox.sendConfig('CFG-HNR', 4, data[0])

        print('\nReadback configuration')
        print('----------------------')
        data = ublox.poll('CFG-HNR', printMessage=True)
