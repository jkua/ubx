#!/usr/bin/env python3

from ubloxMessage import UbloxMessage, CLIDPAIR
import ubloxMessage
from smbus2 import SMBusWrapper
import time
import logging

def printHex(block, header=True):
    numBlocks, remainder = divmod(len(block), 16)

    i = 0
    while i < numBlocks:
        hexString = ' '.join('{:02x}'.format(x) for x in block[16*i:16*i+8])
        hexString += ' '
        hexString += ' '.join('{:02x}'.format(x) for x in block[16*i+8:16*i+16])
        
        if header:    
            hexString = '{:02d}) '.format(i) + hexString

        print(hexString)

        i += 1

    if remainder > 0:
        hexString = ' '.join('{:02x}'.format(x) for x in block[16*i:16*i+8])
        if remainder > 8:
            hexString += ' '
            hexString += ' '.join('{:02x}'.format(x) for x in block[16*i+8:16*i+16])
        if header:
            hexString = '{:02d}) '.format(i) + hexString
        print(hexString)  


class UbloxI2C(object):
    def __init__(self, bus, ubloxAddress=0x42):
        self.bus = bus
        self.deviceAddress = ubloxAddress

    def getNavPvt(self):
        data = self.poll('NAV-PVT', printMessage=printMessage)
        return data

    def getNavStatus(self, printMessage=False):
        data = self.poll('NAV-STATUS', printMessage=printMessage)
        return data[0]

    def reset(self, startType, clear=None, mode='hw'):
        if clear is None:
            if startType == 'hot':
                navBbrMask = 0
            elif startType == 'warm':
                navBbrMask = 1
            elif startType == 'cold':
                navBbrMask = 0xff
        else:
            navBbrMask = UbloxMessage.buildMask(clear, ubloxMessage.navBbrMaskShiftDict)

        resetMode = ubloxMessage.resetModeDict[mode]

        logging.info('Sending restart command... this will not be ACKed.')
        self.sendMessage("CFG-RST", 4, {'nav_bbr': navBbrMask, 'Reset': resetMode})

    def poll(self, messageType, length=0, data=[], printMessage=False):
        logging.info('Polling for {}...'.format(messageType))

        self.clearReceiveBuffer()
        self.sendMessage(messageType, length, data)

        msgType, data, remainder = self.receiveMessage()

        if msgType != messageType:
            raise Exception('Response was of a different type! Got {} instead of {}!'.format(msgType, messageType))

        if remainder is not None:
            logging.debug('Parsing remainder...')
            msgTypeR, dataR, remainder = UbloxMessage.parse(remainder)
            if messageType.startswith('CFG-') and msgTypeR == 'ACK-ACK':
                if self.checkAck(msgTypeR, dataR, messageType):
                    logging.info('Config message ACKed by ublox.')

        if printMessage:
            UbloxMessage.printMessage(msgType, data)

        return data

    def sendConfig(self, messageType, length, data):
        logging.info('Sending {}...'.format(messageType))

        self.clearReceiveBuffer()

        self.sendMessage(messageType, length, data)

        msgType, data, remainder = self.receiveMessage()

        if self.checkAck(msgType, data, messageType):
            logging.info('Config message ACKed by ublox.')

        return None

    def checkAck(self, ackMessageType, ackData, cfgMessageType):
        if ackMessageType == 'ACK-NACK':
            raise Exception('ublox receiver responded with ACK-NACK!')

        if ackMessageType != 'ACK-ACK':
            raise ValueError('This is not an ACK-ACK or ACK-NACK message! ({})\n{}'.format(ackMessageType, ackData))

        clsId, msgId = CLIDPAIR[cfgMessageType]
        if ackData[0]['ClsID'] != clsId or ackData[0]['MsgID'] != msgId:
            raise ValueError('ublox receiver ACKed a different message ({}, {})!'.format(data[0]['ClsID'], data[0]['MsgID']))

        return True

    def sendMessage(self, messageType, length, data):
        rawMessage = UbloxMessage.buildMessage(messageType, length, data)
        self.sendRawMessage(rawMessage)

    def sendRawMessage(self, rawMessage, chunkSize=32):
        while len(rawMessage) > 0:
            self.bus.write_i2c_block_data(self.deviceAddress, 0xff, rawMessage[:chunkSize])
            rawMessage = rawMessage[chunkSize:]

    def receiveMessage(self, timeout=1):
        bytesAvailable = self.waitForMessage(timeout=timeout)

        if bytesAvailable == 0:
            raise Exception('Failed to get response!')
        else:
            logging.debug('Bytes available for read: {}'.format(bytesAvailable))
        
        message = self.readBytes(bytesAvailable)
        msgType, data, remainder = UbloxMessage.parse(message)

        if remainder is not None:
            logging.debug('Extra data in message buffer! ({})'.format(len(remainder)))

        return msgType, data, remainder

    def waitForMessage(self, timeout=1):
        sleepTime = 0.005
        startTime = time.time()
        bytesAvailable = self.readBytesAvailable()
        while bytesAvailable == 0:
            elapsedTime = time.time() - startTime
            
            if elapsedTime > timeout:
                break
            
            if elapsedTime < 0.05:
                pass
            elif elapsedTime < 0.5:
                sleepTime = 0.05
            else:
                sleepTime = 0.1

            time.sleep(sleepTime)
            bytesAvailable = self.readBytesAvailable()

        if bytesAvailable > 0:
            logging.debug('Response in {:.3f} s'.format(time.time()-startTime))

        return bytesAvailable

    def clearReceiveBuffer(self):
        bytesAvailable = self.readBytesAvailable()
        if bytesAvailable > 0:
            logging.info('Dumping buffer [{} bytes]...'.format(bytesAvailable))
            self.readBytes(bytesAvailable)

    def readBytesAvailable(self):
        block = self.bus.read_i2c_block_data(self.deviceAddress, 0xfd, 2)
        bytesAvailable = (block[0] << 8) + block[1]

        return bytesAvailable

    def readBytes(self, numBytes):
        numBlocks, remainder = divmod(numBytes, 32)

        i = 0
        data = []

        while i < numBlocks:
            block = self.bus.read_i2c_block_data(self.deviceAddress, 0xff, 32)
            data.extend(block)
            i += 1

        if remainder > 0:
            block = self.bus.read_i2c_block_data(self.deviceAddress, 0xff, remainder)
            data.extend(block)

        return data


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--bus', '-b', type=int, default=11, help='I2C bus number')
    args = parser.parse_args()

    # logging.basicConfig(level=logging.WARNING)
    logging.basicConfig(level=logging.DEBUG)

    with SMBusWrapper(args.bus) as bus:
        ublox = UbloxI2C(bus)
        data = ublox.poll('MON-VER', printMessage=True)

        data = ublox.poll('NAV-PVT', printMessage=True)

        data = ublox.poll('CFG-PRT', printMessage=True)
        
        if data[1]['Out_proto_mask'] != 1:
            print('\nReconfiguring I2C out proto mask...')
            data[1]['Out_proto_mask'] = 1
            ublox.sendConfig('CFG-PRT', 20, data)

        data = ublox.poll('CFG-PRT', 1, {'PortID': 1}, printMessage=True)

        print('\nReconfiguring UART in proto mask...')
        data[1]['In_proto_mask'] = 3
        ublox.sendConfig('CFG-PRT', 20, data)

        data = ublox.poll('CFG-PRT', 1, {'PortID': 1}, printMessage=True)

        data = ublox.getNavStatus(printMessage=True)

        ublox.reset(None, ['pos', 'sfdr', 'vmon'], 'swGnssOnly')

        data = ublox.getNavStatus(printMessage=True)



