#!/usr/bin/env python3

from ubloxMessage import UbloxMessage, CLIDPAIR
import serial
import serial.threaded
import time
import traceback
import logging

import datetime

class UbloxReader(serial.threaded.Protocol):
    def __init__(self):
        self.buffer = b''
        self.start = 0
        self.pollResult = None
        self.pollTarget = None
        self.printMessageFlag = False
        self.printMessageFilter = None
        self.saveStreamFlag = False
        self.saveStreamFilter = None
        self.saveFormat = 'ubx'
        self.saveFile = None
        self.saveFileName = 'ublox'
        self.userHandler = None
        self.lastFlushTime = None
        self.logger = logging

    # Required for serial.threaded.Protocol
    def connection_made(self, transport):
        super(UbloxReader, self).connection_made(transport)
        self.logger.debug('Serial port opened\n')

    # Required for serial.threaded.Protocol
    def data_received(self, data):
        self.logger.debug('Received {} bytes'.format(len(data)))
        self.buffer = self.buffer + data
        self.logger.debug('Buffer size: {} bytes'.format(len(self.buffer)))
        self.parse()

    # Required for serial.threaded.Protocol
    def connection_lost(self, exc):
        if exc:
            self.logger.error('*** EXCEPTION *** {}'.format(exc))
        self.logger.debug('Serial port closed.')
        if self.saveFile is not None:
            self.saveFile.close()
            self.saveFile = None
            self.logger.debug('Save file closed.')

    # Parse buffer looking for messages
    def parse(self):
        self.logger.debug('in UbloxReader.parse()')
        if len(self.buffer) < 8:
            self.logger.debug('UbloxReader.parse(): not enough data in buffer')
            return
        index = self.buffer.find(b'\xb5\x62')
        if index >= 0:
            self.start += index
            msgTime = time.time()
            self.logger.debug('UbloxReader.parse(): sending for validation')
            result = UbloxMessage.validate(self.buffer[self.start:])
            if result['valid']:
                rawMessage = self.buffer[self.start:]
                self.logger.debug('UbloxReader.parse(): sending to UbloxMessage.parse()')
                msgFormat, msgData, remainder = UbloxMessage.parse(rawMessage)
                rawMessage = rawMessage[:len(rawMessage) - len(remainder)] if remainder is not None else rawMessage[:len(rawMessage)]
                self.buffer = remainder if remainder is not None else b''
                self.start = 0
                if msgFormat is not None:
                    self.logger.debug('UbloxReader.parse(): sending to UbloxReader.handleMessage()')
                    self.handleMessage(msgTime, msgFormat, msgData, rawMessage)
                    return
            else:
                # Invalid message, move past sync bytes
                if result['lengthMatch'] or (result['length'] > 4096):
                    if result['lengthMatch']:
                        self.logger.debug('UbloxReader.parse(): invalid message in buffer, moving past sync')
                    else:
                        self.logger.debug('UbloxReader.parse(): invalid length ({}) - enforcing max length of 4096 bytes'.format(result['length']))
                    self.buffer = self.buffer[self.start+2:]
                    return
                else:
                    self.logger.debug('Ublox.parse(): Header indicates a message of length {}, buffer only has {} bytes'.format(result['length'], len(self.buffer)))
                    return
        # Discard all but the last byte
        else:
            self.logger.debug('UbloxReader.parse(): could not find sync in buffer, discarding all but the last byte')
            self.buffer = self.buffer[-1:]
            self.start = 0
            return

    # Handle a received message
    def handleMessage(self, msgTime, msgFormat, msgData, rawMessage):
        # This is a polled message
        if (self.pollTarget is not None) and (msgFormat in self.pollTarget):
            self.pollResult = (msgFormat, msgData)
            self.pollTarget = None

        # Save message
        if self.saveStreamFlag and (self.saveStreamFilter is None or msgFormat in self.saveStreamFilter):
            self.saveMessage(msgTime, msgFormat, msgData, rawMessage)

        # Print message to screen
        if self.printMessageFlag and (self.printMessageFilter is None or msgFormat in self.printMessageFilter):
            self.printMessage(msgTime, msgFormat, msgData)

        # Call user handler
        if self.userHandler is not None:
            self.userHandler(msgTime, msgFormat, msgData, rawMessage)

    def printMessage(self, msgTime, msgFormat, msgData):
        UbloxMessage.printMessage(msgFormat, msgData, msgTime, fmt='short')

    def saveMessage(self, msgTime, msgFormat, msgData, rawMessage):
        if self.saveInterval is not None:
            if msgFormat == 'NAV-PVT':
                year = msgData[0]['Year']
                month = msgData[0]['Month']
                day = msgData[0]['Day']
                hour = msgData[0]['Hour']
                minute = msgData[0]['Min']
                second = msgData[0]['Sec']
                newFile = False
                if self.saveInterval == 'hourly' and hour != self.curInterval:
                    self.curInterval = hour
                    newFile = True
                elif self.saveInterval == 'daily' and day != self.curInterval:
                    self.curInterval = day
                    newFile = True

                if newFile:
                    if self.saveFile is not None:
                        self.saveFile.close()
                    dt = datetime.datetime(year, month, day, hour, minute, second)
                    filename = '{}_{}.{}'.format(self.saveFileName, dt.strftime('%Y%m%dT%H%M%SZ'), self.saveFormat)
                    self.logger.info('*** Opening save file {} for write'.format(filename))
                    self.saveFile = open(filename, 'wb')
                    self.lastFlushTime = time.time()
        else:
            if self.saveFile is None:
                filename = '{}_{}.{}'.format(self.saveFileName, datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ'), self.saveFormat)
                self.logger.info('*** Opening save file {} for write'.format(filename))
                self.saveFile = open(filename, 'wb')
                self.lastFlushTime = time.time()
        if self.saveFormat == 'ubx' and self.saveFile is not None:
            self.logger.debug('Saving {} message of raw length {}'.format(msgFormat, len(rawMessage)))
            self.saveFile.write(rawMessage)
            if (time.time() - self.lastFlushTime) > 60:
                self.saveFile.flush()
                self.lastFlushTime = time.time()

    def poll(self, ser, msgFormat, length=0, data=[], timeout=0.5, maxRetries=20):
        retries = 0
        while retries < maxRetries:        
            self.pollResult = None
            self.pollTarget = [msgFormat]

            self.logger.info('Polling for {} (attempt {})'.format(msgFormat, retries+1))
            self.sendMessage(ser, msgFormat, length, data)

            startTime = time.time()
            while self.pollResult is None:
                time.sleep(0.01)
                if (time.time() - startTime) > timeout:
                    self.logger.warn('Timeout waiting for response!')
                    break

            if self.pollResult is not None:
                return self.pollResult

            retries += 1

        raise Exception('Failed to get response!')

    def sendConfig(self, ser, msgFormat, length, data, timeout=0.5, maxRetries=20):
        retries = 0
        while retries < maxRetries:
            self.pollResult = None
            self.pollTarget = ['ACK-ACK', 'ACK-NACK']

            self.logger.info('Sending config message {} (attempt {})'.format(msgFormat, retries+1))
            self.sendMessage(ser, msgFormat, length, data)

            startTime = time.time()
            while self.pollResult is None:
                time.sleep(0.01)
                if (time.time() - startTime) > timeout:
                    self.logger.warn('Timeout waiting for ACK')
                    break

            if self.pollResult is not None:
                if self.checkAck(self.pollResult[0], self.pollResult[1], msgFormat):
                    self.logger.info('Config message ACKed by ublox')
                return

            retries += 1

        raise Exception('Failed to set configuration!')

    def sendMessage(self, ser, msgFormat, length, data):
        message = UbloxMessage.buildMessage(msgFormat, length, data)
        ser.write(message)

    def checkAck(self, ackMessageType, ackData, cfgMessageType):
        if ackMessageType == 'ACK-NACK':
            raise Exception('ublox receiver responded with ACK-NACK!')

        if ackMessageType != 'ACK-ACK':
            raise ValueError('This is not an ACK-ACK or ACK-NACK message! ({})\n{}'.format(ackMessageType, ackData))

        clsId, msgId = CLIDPAIR[cfgMessageType]
        if ackData[0]['ClsID'] != clsId or ackData[0]['MsgID'] != msgId:
            raise ValueError('ublox receiver ACKed a different message ({}, {})!'.format(ackData[0]['ClsID'], ackData[0]['MsgID']))

        return True

    def setSaveInterval(self, interval):
        if interval not in ['daily', 'hourly', None]:
            raise Exception('Invalid save interval!')
        self.saveInterval = interval
        self.curInterval = None



if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', '-d', default='/dev/ttyHS1', help='Specify the serial port device to communicate with. e.g. /dev/ttyO5')
    parser.add_argument('--loop', '-l', action='store_true', help='Keep sending requests in a loop')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    ser = serial.Serial(args.device, 115200, timeout=1)

    with serial.threaded.ReaderThread(ser, UbloxReader) as protocol:
        while True:
            try:
                msgFormat, msgData = protocol.poll(ser, 'MON-VER')
                UbloxMessage.printMessage(msgFormat, msgData, header=datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S.%f]\n'))
                time.sleep(0.1)
            except KeyboardInterrupt:
                break
