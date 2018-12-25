#!/usr/bin/env python3

from ublox2 import UbloxReader
from ubloxMessage import UbloxMessage, clearMaskShiftDict, CLIDPAIR
import serial
import serial.threaded
import time
import datetime
import calendar
import logging
import os

fixTypeDict = {0: 'NO', 1: 'DR', 2: '2D', 3: '3D', 4: '3D+DR', 5: 'Time'}
fusionModeDict = {0: 'INIT', 1: 'ON', 2: 'Suspended', 3: 'Disabled'}
timeValidDict = {0: 'Invalid', 
                 1: 'Valid Date', 
                 2: 'Valid Time', 
                 3: 'Valid Date+Time', 
                 4: 'Fully Resolved',
                 5: 'Fully Resolved',
                 6: 'Fully Resolved',
                 7: 'Fully Resolved'}
timeValidSymbolDict = {0: 'X', 
                       1: 'D', 
                       2: 'T', 
                       3: 'DT', 
                       4: '',
                       5: '',
                       6: '',
                       7: ''}

timestamp = 0
epoch = 0
dt = datetime.datetime.utcfromtimestamp(0)
offset = 0
lat = 0
lon = 0
alt = 0
speed = 0
hAcc = 0
vAcc = 0
hdop = None
numSats = None
avgCNO = None
fix = 'No'
timeValid = 0
msSinceStartup = None
output = None
display = True
outputFile = None
dataRate = None
dataRateStartTime = None
dataCaptured = 0

# port: 0=DDC(I2C), 1=UART1, 3=USB, 4=SPI
def setMessageRate(ser, ublox, messageType, rate, port=None):
    messageClass, messageId = CLIDPAIR[messageType]
    if port is None:
        ublox.sendConfig(ser, 'CFG-MSG', 3, {'msgClass': messageClass, 'msgId': messageId, 'rate': rate})
    else:
        msgFormat, msgData = ublox.poll(ser, 'CFG-MSG', 2, {'msgClass': messageClass, 'msgId': messageId})
        msgData[port+1]['rate'] = rate
        ublox.sendConfig(ser, msgFormat, 8, msgData)

def messageHandler(msgTime, msgFormat, msgData, rawMessage):
    global dataRate, dataRateStartTime, dataCaptured, timestamp, epoch, dt, offset, lat, lon, alt, speed, hAcc, vAcc, hdop, numSats, avgCNO, fix, timeValid, output, display, dataRate, msSinceStartup

    curTimestamp = time.time()

    if dataRateStartTime is None:
        dataRateStartTime = time.time()
    else:
        dataCaptured += len(rawMessage)
        curTime = time.time()
        elapsed = curTime - dataRateStartTime
        if elapsed > 2:
            dataRate = dataCaptured / elapsed * 8
            dataCaptured = 0
            dataRateStartTime = curTime

    logging.info(msgFormat)

    if msgFormat == 'NAV-PVT':
        epoch = msgData[0]['ITOW']/1e3
        
        year = msgData[0]['Year']
        month = msgData[0]['Month']
        day = msgData[0]['Day']
        hour = msgData[0]['Hour']
        minute = msgData[0]['Min']
        second = msgData[0]['Sec']
        nano = msgData[0]['Nano']
        dt = datetime.datetime(year, month, day, hour, minute, second) + datetime.timedelta(microseconds=int(nano / 1000.))
        timestamp = calendar.timegm(dt.timetuple()) + dt.microsecond * 1e-6
        timeValid = msgData[0]['Valid'] & 0x7
        # timeValidSymbol = str(timeValid)
        offset = curTimestamp - timestamp

        lat = msgData[0]['LAT']/1e7
        lon = msgData[0]['LON']/1e7
        alt = msgData[0]['HEIGHT']/1e3
        heading = msgData[0]['HeadVeh']/1e5
        speed = msgData[0]['GSpeed']/1e3
        fix = fixTypeDict[msgData[0]['FixType']]
        hAcc = msgData[0]['Hacc']/1e3
        vAcc = msgData[0]['Vacc']/1e3

    elif msgFormat == 'NAV-SVINFO':
        cno = []
        for satInfo in msgData[1:]:
            if satInfo['Flags'] & 1:
                cno.append(satInfo['CNO'])
        numSats = len(cno)
        if len(cno):
            avgCNO = float(sum(cno)) / len(cno)
        else:
            avgCNO = 0

    elif msgFormat == 'NAV-STATUS':
        # print('NAV-STATUS time: {:.3f}'.format(msgData[0]['ITOW']/1e3))
        fix = fixTypeDict[msgData[0]['GPSfix']]
        msSinceStartup = msgData[0]['MSSS']

        speedMph = speed / 0.44704

        timeValidSymbol = timeValidSymbolDict[timeValid]
        timeString = timeValidSymbol + dt.strftime('%H:%M:%S') + '.{:03.0f}Z'.format(dt.microsecond/1000.)
        numSatsString = '--' if numSats is None else '{:2}'.format(numSats)
        hdopString = '--' if hdop is None else '{:.1f}'.format(hdop)
        cnoString = '--' if avgCNO is None else '{:.1f}'.format(avgCNO)
        msssString = '--' if msSinceStartup is None else '{:.3f}'.format(msSinceStartup/1e3)
        displayString = '[{} {:.3f} ({:.3f}) | {:.3f} | {}] Pos: {:.7f}, {:.7f}, {:.3f}'.format(timeString, timestamp, offset, epoch, msssString, lat, lon, alt)
        displayString += ' | Fix: {}, # Sats: {}, CNO: {}, HAcc: {:.3f}, VAcc: {:.3f}'.format(fix, numSatsString, cnoString, hAcc, vAcc) 
        displayString += ' | {:.1f} MPH'.format(speedMph)
        if dataRate is not None:
            displayString += ' | Data rate: {:.1f} Kbps'.format(dataRate/1000)
        print(displayString)
        logging.info(displayString)
    # if msgFormat in ['NAV-PVT', 'NAV-STATUS', 'NAV-SVINFO']:
    #     print(msgData)

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', '-d', default='/dev/ttyHS1', help='Specify the serial port device to communicate with. e.g. /dev/ttyO5')
    parser.add_argument('--output', '-o', help='Specify output path')
    parser.add_argument('--configure', '-c', action='store_true', help='Configure the receiver')
    parser.add_argument('--interval', '-i', choices=['daily', 'hourly'], default=None, help='Specify file interval (daily, hourly)')
    parser.add_argument('--logFile', '-l', help='Path to log file')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logLevel = logging.DEBUG
    else:
        logLevel = logging.INFO

    logging.basicConfig(filename=args.logFile, level=logLevel, format='%(asctime)s %(message)s')

    logging.info('***** Session start *****')

    ser = serial.Serial(args.device, 921600, timeout=1)
    with serial.threaded.ReaderThread(ser, UbloxReader) as ublox:
        if args.output is not None:
            ublox.saveFileName = os.path.join(args.output, 'ublox')
        ublox.setSaveInterval(args.interval)
        ublox.printMessageFlag = True
        ublox.userHandler = messageHandler

        if args.configure:
            print('*** Configuring receiver...')
            # Set measurement rate to 1 Hz during config to prevent problems
            print('Setting measurement rate to 1 Hz...')
            ublox.sendConfig(ser, 'CFG-RATE', 6, {'Meas': 1000, 'Nav': 1, 'Time': 1})

            # Reset to default config
            clearMask = UbloxMessage.buildMask(['msgConf'], clearMaskShiftDict)
            print('Restoring message configuration...')
            ublox.sendConfig(ser, 'CFG-CFG', 12, {'clearMask': clearMask, 'saveMask': 0, 'loadMask': clearMask})

            # Set power management settings
            print('Setting power management to full power...')
            ublox.sendConfig(ser, 'CFG-PMS', 8, {'Version': 0, 'PowerSetupValue': 0, 'Period': 0, 'OnTime': 0})            
            
            # Disable NMEA output - UBX only
            print('Polling for port config (CFG-PRT)...')
            msgFormat, msgData = ublox.poll(ser, 'CFG-PRT')
            UbloxMessage.printMessage(msgFormat, msgData)
            print('Disabling NMEA output (CFG-PRT)...')
            msgData[1]["Out_proto_mask"] = 1
            ublox.sendConfig(ser, msgFormat, 20, msgData)

            # Enable messages
            rate = 1
            messageList = [('NAV-PVT', 1), ('NAV-STATUS', 1), ('NAV-SVINFO', 1), ('RXM-RAWX', 1), ('RXM-SFRBX', 1)]
            for message, rate in messageList:
                print('Enabling {} message...'.format(message))
                setMessageRate(ser, ublox, message, rate)
            
            # Set measurement rate to 5 
            print('Setting measurement rate to 5 Hz...')
            ublox.sendConfig(ser, 'CFG-RATE', 6, {'Meas': 200, 'Nav': 5, 'Time': 1})

            print('*** Configuration complete!')


        ublox.saveStreamFlag = True
        while 1:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break


