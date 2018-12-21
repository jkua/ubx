#!/usr/bin/env python3

from ubloxMessage import UbloxMessage
import datetime
import os.path

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('--datetime', help="UTC datetime in ISO8601 format YYYYMMDDTHHMMSS.fff")
    args = parser.parse_args()

    index = args.datetime.find('.')
    if index >= 0:
        dtString = args.datetime[:index]
        fractionalSeconds = float(args.datetime[index:])
    else:
        dtString = args.datetime
        fractionalSeconds = 0

    dt = datetime.datetime.strptime(dtString, '%Y%m%dT%H%M%S')
    dt += datetime.timedelta(seconds=fractionalSeconds)

    print('Split time: {}'.format(dt.strftime('%Y-%m-%d %H:%M:%S.%f')))

    filenameNoExt, ext = os.path.splitext(args.input)
    f = open(args.input, 'rb')
    data = f.read()

    outputFile = open('{}_part1'.format(filenameNoExt) + ext, 'wb')
    start = 0
    numMessages = 0
    split = False
    while start < (len(data) - 8):
        rawMessage, msgClass, msgId, length, start = UbloxMessage.getMessageFromBuffer(data, start)
        if rawMessage is not None:
            payload = rawMessage[6:length+6]
            try:
                msgFormat, msgData = UbloxMessage.decode(msgClass, msgId, length, payload)
            except ValueError:
                continue

            UbloxMessage.printMessage(msgFormat, msgData, None, fmt='short')

            if msgFormat == 'NAV-PVT':
                curDt = datetime.datetime(msgData[0]['Year'], msgData[0]['Month'], msgData[0]['Day'], 
                                          msgData[0]['Hour'], msgData[0]['Min'], msgData[0]['Sec'])
                curDt += datetime.timedelta(microseconds=msgData[0]['Nano']/1e3)

                if not split and (curDt > dt):
                    # print('splitDt: {}, curDt: {}'.format(dt, curDt))
                    print('**** SPLIT ****')
                    outputFile.close()
                    numMessages1 = numMessages
                    numMessages = 0
                    outputFile = open('{}_part2'.format(filenameNoExt) + ext, 'wb')
                    split = True

            numMessages += 1
            outputFile.write(rawMessage)

    numMessages2 = numMessages
    outputFile.close()

    print('\n# messages before split: {}, after: {}'.format(numMessages1, numMessages2))