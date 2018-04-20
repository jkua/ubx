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

fixTypeDict = {0: 'NO', 1: 'DR', 2: '2D', 3: '3D', 4: '3D+DR', 5: 'Time'}
fusionModeDict = {0: 'INIT', 1: 'ON', 2: 'Suspended', 3: 'Disabled'}

time = 0
lat = 0
lon = 0
alt = 0
speed = 0
roll = 0
pitch = 0
heading = 0
hdop = 0
numSats = 0
avgCNO = 0
fix = 'No'
fusionMode = 'Unknown'
output = None
display = True

def callback(ty, packet):
    global time, lat, lon, alt, speed, roll, pitch, heading, hdop, numSats, avgCNO, fix, fusionMode, output

    if output is not None:
        if ty not in output:
            output[ty] = []
        output[ty].append(packet)

    if ty == 'HNR-PVT':
        time = packet[0]['ITOW']/1e3
        lat = packet[0]['LAT']/1e7
        lon = packet[0]['LON']/1e7
        alt = packet[0]['HEIGHT']/1e3
        heading = packet[0]['HeadVeh']/1e5
        speed = packet[0]['Speed']/1e3
        fix = fixTypeDict[packet[0]['GPSFix']]
    
        speedMph = speed / 0.44704
        if display:
            print('[{:.3f}] Pos: {:.6f}, {:.6f}, {:.3f} | R: {:.1f}, P: {:.1f}, Hdg {:.1f} | Fix: {}, # Sats: {:2}, CNO: {:.1f}, HDOP: {:.1f}, Fusion: {} | {:.1f} MPH'.format(time, lat, lon, alt, roll, pitch, heading, fix, numSats, avgCNO, hdop, fusionMode, speedMph))

    elif ty == 'NAV-ATT':
        roll = packet[0]['Roll']/1e5
        pitch = packet[0]['Pitch']/1e5
        heading = packet[0]['Heading']/1e5
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
        print("{}: {}".format(ty, packet))
    else:
        return

    # if ty.startswith('$'):
    #     print packet
    # else:
    #     print("{}: {}".format(ty, packet))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--device', '-d', default=None)
    group.add_argument('--file', '-f', default=None)
    parser.add_argument('--output', '-o', default=None)
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.WARNING)

    if args.device:
        t = ubx.Parser(callback, device=args.device)
        gobject.MainLoop().run()
    else:
        if args.output is not None:
            display = False
            output = {}
        t = ubx.Parser(callback, device=False)
        binFile = args.file
        data = open(binFile,'r').read()
        t.parse(data)

    if args.output is not None:
        for key in sorted(output.keys()):
            print('{}: {}'.format(key, len(output[key])))

        with open(args.output, 'w') as f:
            import cPickle as pickle
            pickle.dump(output, f, pickle.HIGHEST_PROTOCOL)
