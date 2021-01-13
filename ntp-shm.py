#!/usr/bin/env python
# Copyright (C) 2010 Timo Juhani Lindfors <timo.lindfors@iki.fi>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import ubx
import struct
import calendar
import os
import gobject
import logging
import sys
import socket
import time
import datetime
import calendar
from gpsTimestamps import gpsWeekAndTow
import ntpdshm

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
lat = 0
lon = 0
alt = 0
speed = 0
attTime = None
roll = None
pitch = None
heading = None
hdop = None
numSats = None
avgCNO = None
fix = 'No'
fusionMode = 'Unknown'
msSinceStartup = None
output = None
display = True
outputFile = None
dataRate = None
dataRateStartTime = None
dataCaptured = 0
ntpd_shm = ntpdshm.NtpdShm(unit=0)
ntpd_shm.mode = 0
ntpd_shm.precision = -6
ntpd_shm.leap = 0

def callback(ty, packet):
    global timestamp, lat, lon, alt, speed, attTime, roll, pitch, heading, hdop, numSats, avgCNO, fix, fusionMode, output, display, dataRate, msSinceStartup

    curTimestamp = time.time()

    if args.raw:
        print('{}: {}'.format(ty, packet))

    if ty == 'NAV-PVT':
        epoch = packet[0]['ITOW']/1e3

        year = packet[0]['Year']
        month = packet[0]['Month']
        day = packet[0]['Day']
        hour = packet[0]['Hour']
        minute = packet[0]['Min']
        second = packet[0]['Sec']
        nano = packet[0]['Nano']
        dt = datetime.datetime(year, month, day, hour, minute, second) + datetime.timedelta(microseconds=int(nano / 1000.))
        timestamp = calendar.timegm(dt.timetuple()) + dt.microsecond * 1e-6
        timeValid = packet[0]['Valid'] & 0x7
        timeValidSymbol = timeValidSymbolDict[timeValid]
        # timeValidSymbol = str(timeValid)
        offset = curTimestamp - timestamp

        if timeValid == 7:
            print('Updating NTP with timestamp: {}'.format(timestamp))
            ntpd_shm.update(timestamp)
        else:
            print('Time not valid, not updating NTP')
        lat = packet[0]['LAT']/1e7
        lon = packet[0]['LON']/1e7
        alt = packet[0]['HEIGHT']/1e3
        heading = packet[0]['HeadVeh']/1e5
        speed = packet[0]['GSpeed']/1e3
        fix = fixTypeDict[packet[0]['FixType']]
    
        speedMph = speed / 0.44704
        if display:
            timeString = timeValidSymbol + dt.strftime('%H:%M:%S') + '.{:03.0f}Z'.format(dt.microsecond/1000.)
            numSatsString = '--' if numSats is None else '{:2}'.format(numSats)
            attTimeString = '--' if attTime is None else '{:.3f}'.format(attTime)
            rollString = '--' if roll is None else '{:.3f}'.format(roll)
            pitchString = '--' if pitch is None else '{:.3f}'.format(pitch)
            hdopString = '--' if hdop is None else '{:.1f}'.format(hdop)
            cnoString = '--' if avgCNO is None else '{:.1f}'.format(avgCNO)
            msssString = '--' if msSinceStartup is None else '{:.3f}'.format(msSinceStartup/1e3)
            displayString = '[{} {:.3f} ({:.3f}) | {:.3f} | {}] Pos: {:.6f}, {:.6f}, {:.3f}'.format(timeString, timestamp, offset, epoch, msssString, lat, lon, alt)
            displayString += ' | Att Time: {}, R: {}, P: {}, Hdg {:.1f}'.format(attTimeString, rollString, pitchString, heading)
            displayString += ' | Fix: {}, # Sats: {}, CNO: {}, HDOP: {}, Fusion: {}'.format(fix, numSatsString, cnoString, hdopString, fusionMode) 
            displayString += ' | {:.1f} MPH'.format(speedMph)
            if dataRate is not None:
                displayString += ' | Data rate: {:.1f} Kbps'.format(dataRate/1000)
            print(displayString)

    else:
        return

def rawCallback(data):
    global outputFile, dataRate, dataRateStartTime, dataCaptured
    if outputFile is not None:
        outputFile.write(data)
    if args.raw:
        dataRateString = '{:.3f} Kbps'.format(dataRate) if dataRate is not None else '--'
        print('Data rate: {}, Data [{}]: {}'.format(dataRateString, len(data), repr(data)))
    if dataRateStartTime is None:
        dataRateStartTime = time.time()
    else:
        dataCaptured += len(data)
        curTime = time.time()
        elapsed = curTime - dataRateStartTime
        if elapsed > 2:
            dataRate = dataCaptured / elapsed * 8
            dataCaptured = 0
            dataRateStartTime = curTime

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--device', '-d', default='/dev/ttyHS1')
    group.add_argument('--file', '-f', default=None)
    parser.add_argument('--output', '-o', default=None)
    parser.add_argument('--raw', action='store_true')
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.WARNING)

    if args.output is not None:
        outputFile = open(args.output, 'wb')

    if args.device:
        t = ubx.Parser(callback, device=args.device, rawCallback=rawCallback)
        try:
            gobject.MainLoop().run()
        except KeyboardInterrupt:
            gobject.MainLoop().quit()
            if outputFile is not None:
                outputFile.close()
    else:
        t = ubx.Parser(callback, device=False)
        binFile = args.file
        data = open(binFile,'r').read()
        t.parse(data)
