#!/usr/bin/env python3

from smbus2 import SMBusWrapper
from ubloxI2c import UbloxI2C
import logging
import time

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--bus', '-b', type=int, default=11, help='I2C bus number')
    parser.add_argument('--loop', '-l', action='store_true', help='Keep sending requests in a loop')
    args = parser.parse_args()

    # logging.basicConfig(level=logging.WARNING)
    logging.basicConfig(level=logging.DEBUG)

    with SMBusWrapper(args.bus) as bus:
        ublox = UbloxI2C(bus)

        while True:
            try:
                data = ublox.poll('NAV-SAT', printMessage=False, timeout=5, delay=0.5)
            except KeyboardInterrupt:
                break
            
            if not args.loop:
                break

            time.sleep(0.1)
