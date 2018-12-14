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
    parser.add_argument('--mode', type=int)
    parser.add_argument('--baudrate', type=int)
    parser.add_argument('--inProtoMask', type=int)
    parser.add_argument('--outProtoMask', type=int)
    parser.add_argument('--flags', type=int)
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

        print('\nCurrent configuration')
        print('---------------------')
        data = ublox.poll('CFG-PRT', 1, {'PortID': portId}, printMessage=True)
        
        if args.mode is not None and args.port != 'usb':
            data[1]['Mode'] = args.mode
        if args.baudrate is not None and args.port == 'uart1':
            data[1]['Baudrate'] = args.baudrate
        if args.inProtoMask is not None:
            data[1]['In_proto_mask'] = args.inProtoMask
        if args.outProtoMask is not None:
            data[1]['Out_proto_mask'] = args.outProtoMask
        if args.flags is not None and args.port != 'usb':
            data[1]['Flags'] = args.flags
            
        ublox.sendConfig('CFG-PRT', 20, data)

        print('\nReadback configuration')
        print('----------------------')
        data = ublox.poll('CFG-PRT', 1, {'PortID': portId}, printMessage=True)
