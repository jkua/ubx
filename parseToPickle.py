#!/usr/bin/python
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

from stream import fixTypeDict, fusionModeDict, timeValidDict, timeValidSymbolDict

dt = None
timestamp = 0
lat = 0
lon = 0
alt = 0
speed = 0
roll = None
pitch = None
heading = None
hdop = None
numSats = None
avgCNO = None
fix = 'No'
fusionMode = 'Unknown'
output = None
display = True
dataRate = None
dataRateStartTime = None
intervalDataProcessed = 0
dataSize = None
dataProcessed = 0


def callback(ty, packet):
    global dt, timestamp, lat, lon, alt, speed, roll, pitch, heading, hdop, numSats, avgCNO, fix, fusionMode, output, dataProcessed, dataRate, dataSize

    if output is not None:
        if ty not in output:
            output[ty] = []
        output[ty].append(packet)

    if ty == 'HNR-PVT':
        epoch = packet[0]['ITOW']/1e3
        
        year = packet[0]['Year']
        month = packet[0]['Month']
        day = packet[0]['Day']
        hour = packet[0]['Hour']
        minute = packet[0]['Min']
        second = packet[0]['Sec']
        nano = packet[0]['Nano']
        dt = datetime.datetime(year, month, day, hour, minute, second) + datetime.timedelta(microseconds=nano/1000.)
        timestamp = calendar.timegm(dt.timetuple())
        timeValid = packet[0]['Valid'] & 0x7
        timeValidSymbol = timeValidSymbolDict[timeValid]
        # timeValidSymbol = str(timeValid)

        lat = packet[0]['LAT']/1e7
        lon = packet[0]['LON']/1e7
        alt = packet[0]['HEIGHT']/1e3
        heading = packet[0]['HeadVeh']/1e5
        speed = packet[0]['Speed']/1e3
        fix = fixTypeDict[packet[0]['GPSFix']]
    
        speedMph = speed / 0.44704
        if display:
            timeString = timeValidSymbol + dt.strftime('%H:%M:%S') + '.{:03.0f}Z'.format(dt.microsecond/1000.)
            numSatsString = '--' if numSats is None else '{:2}'.format(numSats)
            rollString = '--' if roll is None else '{:.3f}'.format(roll)
            pitchString = '--' if pitch is None else '{:.3f}'.format(pitch)
            hdopString = '--' if hdop is None else '{:.1f}'.format(hdop)
            cnoString = '--' if avgCNO is None else '{:.1f}'.format(avgCNO)
            displayString = '[{}] Pos: {:.6f}, {:.6f}, {:.3f}'.format(timeString, lat, lon, alt)
            displayString += ' | R: {}, P: {}, Hdg {:.1f}'.format(rollString, pitchString, heading)
            displayString += ' | Fix: {}, # Sats: {}, CNO: {}, HDOP: {}, Fusion: {}'.format(fix, numSatsString, cnoString, hdopString, fusionMode) 
            displayString += ' | {:.1f} MPH'.format(speedMph)
            displayString += ' | Processed {:.0f}/{:.0f} KB ({:.3f} %)'.format(dataProcessed/1000., dataSize/1000., float(dataProcessed)/dataSize * 100)
            if dataRate is not None:
                displayString += ', Rate: {:.1f} KB/s'.format(dataRate/1000.)
            print(displayString)

    # elif ty == 'NAV-PVT':
    #     if dt is not None and dt > datetime.datetime(2019, 11, 8, 22, 49, 50):
    #         logging.basicConfig(level=logging.DEBUG)
    #         print('NAV-PVT - ITOW: {}'.format(packet[0]['ITOW']))
    #         import pdb; pdb.set_trace()

    elif ty == 'NAV-ATT':
        roll = packet[0]['Roll']/1e5
        pitch = packet[0]['Pitch']/1e5
        # heading = packet[0]['Heading']/1e5
    elif ty == 'NAV-DOP':
        hdop = packet[0]['HDOP']/100.
    elif ty == 'NAV-STATUS':
        fix = fixTypeDict[packet[0]['GPSfix']]
    elif ty == 'NAV-SVINFO':
        cno = []
        for satInfo in packet[1:]:
            if satInfo['Flags'] & 1:
                cno.append(satInfo['CNO'])
        numSats = len(cno)
        if len(cno):
            avgCNO = float(sum(cno)) / len(cno)
        else:
            avgCNO = 0
    elif ty == 'ESF-STATUS':
        fusionMode = fusionModeDict[packet[0]['FusionMode']]
        # print("{}: {}".format(ty, packet))
    else:
        return

    # if ty.startswith('$'):
    #     print packet
    # else:
    #     print("{}: {}".format(ty, packet))

def rawCallback(data):
    global dataProcessed, dataRate, intervalDataProcessed, dataRateStartTime

    if dataRateStartTime is None:
        dataRateStartTime = time.time()
    else:
        dataProcessed += len(data)
        intervalDataProcessed += len(data)
        curTime = time.time()
        elapsed = curTime - dataRateStartTime
        if elapsed > 1:
            dataRate = intervalDataProcessed / elapsed
            intervalDataProcessed = 0
            dataRateStartTime = curTime

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='UBX file to parse')
    parser.add_argument('--output', '-o', default=None)
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.WARNING)

    if args.output is None:
        head, ext = os.path.splitext(args.file)
        args.output = head + '.pickle'
        
    display = True
    output = {}
    t = ubx.Parser(callback, device=False, rawCallback=rawCallback)
    binFile = args.file
    data = open(binFile,'rb').read()
    dataSize = len(data)
    t.parse(data, useRawCallback=True)

    for key in sorted(output.keys()):
        print('{}: {}'.format(key, len(output[key])))

    with open(args.output, 'wb') as f:
        import pickle
        pickle.dump(output, f, pickle.HIGHEST_PROTOCOL)
