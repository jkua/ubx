#!/usr/bin/env python3

from smbus2 import SMBusWrapper
from ubloxI2c import UbloxI2C
import logging
import time

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--bus', '-b', type=int, default=11, help='I2C bus number')
    parser.add_argument('--port', '-p', choices=['ddc', 'i2c', 'uart1', 'usb', 'spi'], default='i2c')
    parser.add_argument('--loop', '-l', action='store_true', help='Keep sending requests in a loop')
    args = parser.parse_args()

    # logging.basicConfig(level=logging.WARNING)
    logging.basicConfig(level=logging.DEBUG)

    portNameToPortId = {'ddc': 0, 'i2c': 0,
                        'uart1': 1,
                        'usb': 3,
                        'spi': 4
                        }
    portId = portNameToPortId[args.port]
    with SMBusWrapper(args.bus) as bus:
        ublox = UbloxI2C(bus)

        while True:
            try:
                data = ublox.poll('CFG-PRT', 1, {'PortID': portId}, printMessage=True)
            except KeyboardInterrupt:
                break
            
            if not args.loop:
                break

            time.sleep(0.1)
