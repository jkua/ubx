#!/usr/bin/env python3

from ubloxMessage import UbloxMessage
import datetime
import os.path

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    args = parser.parse_args()

    inputDirectory, tail = os.path.split(args.input)
    f = open(args.input, 'rb')
    data = f.read()

    outputFile = open(os.path.join(inputDirectory, 'ublox_solution.pos'), 'wt')
    outputFile.write('%  UTC                   latitude(deg) longitude(deg)  height(m)   Q  ns   sdn(m)   sde(m)   sdu(m)  sdne(m)  sdeu(m)  sdun(m) age(s)  ratio\n')
    
    start = 0
    numMessages = 0
    numNavPvtMessages = 0
    while start < (len(data) - 8):
        rawMessage, msgClass, msgId, length, start = UbloxMessage.getMessageFromBuffer(data, start)
        if rawMessage is not None:
            payload = rawMessage[6:length+6]
            try:
                msgFormat, msgData = UbloxMessage.decode(msgClass, msgId, length, payload)
            except ValueError:
                continue

            UbloxMessage.printMessage(msgFormat, msgData, None, fmt='short')

            numMessages += 1

            if msgFormat == 'NAV-PVT':
                sdne = sdeu = sdun = 99.9999
                age = ratio = 0.
                curDt = datetime.datetime(msgData[0]['Year'], msgData[0]['Month'], msgData[0]['Day'], 
                                          msgData[0]['Hour'], msgData[0]['Min'], msgData[0]['Sec'])
                curDt += datetime.timedelta(microseconds=msgData[0]['Nano']/1e3)
                line = curDt.strftime('%Y/%m/%d %H:%M:%S') + '.{:03.0f}'.format(curDt.microsecond/1e3)
                line += ' '
                line += '{:14.9f} {:14.9f} {:10.4f}'.format(msgData[0]['LAT']/1e7, msgData[0]['LON']/1e7, msgData[0]['HEIGHT']/1e3)
                line += ' {:3d} {:3d} {:8.4f} {:8.4f} {:8.4f}'.format(5, msgData[0]['NumSV'], msgData[0]['Hacc']/1e3, msgData[0]['Hacc']/1e3, msgData[0]['Vacc']/1e3)
                line += ' {:8.4f} {:8.4f} {:8.4f} {:6.2f} {:6.1f}'.format(sdne, sdeu, sdun, age, ratio)
                line += '\n'
                outputFile.write(line)

                numNavPvtMessages += 1

    outputFile.close()

    print('\nNAV-PVT messages: {}/{}'.format(numNavPvtMessages, numMessages))