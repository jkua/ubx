#!/usr/bin/env python3

from smbus2 import SMBusWrapper
from ubloxI2c import UbloxI2C
from ubloxMessage import UbloxMessage
import logging
import time

def extractMessages(data):
    messages = []
    while data is not None:
        msgFormat, msgData, remainder = UbloxMessage.parse(data, raw=True)

        print('{} message of length {}'.format(msgFormat, len(msgData)))
        messages.append((msgFormat, msgData))

        data = remainder

    return messages

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('assistNowFile', help='AssistNow data file')
    parser.add_argument('--bus', '-b', type=int, default=11, help='I2C bus number')
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    #logging.basicConfig(level=logging.DEBUG)

    with open(args.assistNowFile, 'rb') as f:
        data = f.read()

    print('\nRead {} bytes.'.format(len(data)))

    messages = extractMessages(data)

    print('\nRead {} messages.'.format(len(messages)))

    with SMBusWrapper(args.bus) as bus:
        ublox = UbloxI2C(bus)
        print(' ')
        for i, (msgFormat, rawMessage) in enumerate(messages, 1):
            print('Sending {}/{}: {}'.format(i, len(messages), msgFormat))
            ublox.sendRawMessage(rawMessage)
            time.sleep(0.1)

    print('Done.')