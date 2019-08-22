#!/usr/bin/python
"""
Open GPS Daemon - UBX parser class

(C) 2016 Berkeley Applied Analytics <john.kua@berkeleyappliedanalytics.com>
(C) 2010 Timo Juhani Lindfors <timo.lindfors@iki.fi>
(C) 2008 Daniel Willmann <daniel@totalueberwachung.de>
(C) 2008 Openmoko, Inc.
GPLv2
"""
import struct
import calendar
import os
import gobject
import logging
import sys
import socket
import time
from ubloxMessage import UbloxMessage, SYNC1, SYNC2, clearMaskShiftDict, navBbrMaskShiftDict, resetModeDict, powerSetupValueDict, timeRefDict

class Parser():
    def __init__(self, callback, rawCallback=None, device="/dev/ttyO5"):
        self.callback = callback
        self.rawCallback = rawCallback
        self.device = device
        if device:
            os.system("stty -F %s raw" % device)
            self.fd = os.open(device, os.O_NONBLOCK | os.O_RDWR)
            self.flush()
            gobject.io_add_watch(self.fd, gobject.IO_IN, self.cbDeviceReadable)
        self.buffer = ""
        self.ack = {"CFG-PRT" : 0}
        self.ubx = {}

    def cbDeviceReadable(self, source, condition):
        data = os.read(source, 512)
        if self.rawCallback:
            self.rawCallback(data)
        self.parse(data)
        return True

    def setBaudRate(self, baudRate):
        os.close(self.fd)
        os.system('stty -F {} {} cs8 -cstopb -parenb'.format(self.device, baudRate))
        self.fd = os.open(self.device, os.O_NONBLOCK | os.O_RDWR)
        self.flush()
        # time.sleep(0.1)

    def flush(self, quiet=True):
        try:
            buf = os.read(self.fd, 512) # flush input
            if not quiet:
                print("flushed %s" % repr(buf))
        except:
            pass

    def parse(self, data, useRawCallback=False):
        self.buffer += data
        buffer_offset = 0
        # Minimum packet length is 8
        while len(self.buffer) >= buffer_offset + 8:
            # Find the beginning of a UBX message
            start = self.buffer.find( chr( SYNC1 ) + chr( SYNC2 ), buffer_offset )

            # Could not find message - keep data because there may be a whole or partial NMEA message
            # Consider limiting max buffer size
            if start == -1:
                return True

            # Message shorter than minimum length - return and wait for additional data
            # Consider limiting max buffer size
            if start + 8 > len(self.buffer):
                return True

            # Decode header - message class, id, and length
            (cl, id, length) = struct.unpack("<BBH", self.buffer[start+2:start+6])

            # Check that there is enough data in the buffer to match the length
            # If not, return and wait for additional data
            if len(self.buffer) < start + length + 8:
                return True

            # Validate checksum  - if fail, skip past the sync
            if self.checksum(self.buffer[start+2:start+length+6]) != struct.unpack("<BB", self.buffer[start+length+6:start+length+8]):
                buffer_offset = start + 2
                continue

            # At this point, we should have a valid message at the start position

            # Handle data prior to UBX message
            if start > 0:
                logging.debug("Discarded data not UBX %s" % repr(self.buffer[:start]) )
                # Attempt to decode NMEA on discarded data
                self.decodeNmeaBuffer(self.buffer[:start])

            if length == 0:
                logging.warning('Zero length packet of class {}, id {}!'.format(hex(cl), hex(id)))
            else:
                # Decode UBX message
                try:
                    msgFormat, data = UbloxMessage.decode(cl, id, length, self.buffer[start+6:start+length+6])
                except ValueError:
                    data = None
                    pass

                if data is not None:
                    logging.debug("Got UBX packet of type %s: %s" % (msgFormat, data))
                    self.callback(msgFormat, data)
                
            if useRawCallback and (self.rawCallback is not None):
                self.rawCallback(self.buffer[:start+length+8])

            # Discard packet
            self.buffer = self.buffer[start+length+8:]
            buffer_offset = 0

    def send( self, clid, length, payload ):
        logging.debug("Sending UBX packet of type %s: %s" % ( clid, payload ) )
        stream = UbloxMessage.buildMessage(clid, length, payload)
        self.sendraw(stream)

    def sendraw(self, data):
        #print("write %s" % repr(data))
        #print("echo -en \"%s\" > /dev/ttySAC1" % "".join(["\\x%02x" % ord(x) for x in data]))
        os.write(self.fd, data)

    def checksum( self, msg ):
        ck_a = 0
        ck_b = 0
        for i in msg:
            ck_a = ck_a + ord(i)
            ck_b = ck_b + ck_a
        ck_a = ck_a % 256
        ck_b = ck_b % 256
        return (ck_a, ck_b)

    def seekToNextUbxMessage(self, buf):
        start = buf.find(chr( SYNC1 ) + chr( SYNC2 ))
        return buf[start:]

    def decodeNmeaBuffer(self, buf):
        # This assumes the data buffer is NMEA data and looks for messages
        messages = UbloxMessage.decodeNmeaBuffer(buf)

        for message in messages:
            if len(message) == 0:
                continue

            self.callback(message[:start], message)

