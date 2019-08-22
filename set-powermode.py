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


# Set logging rate (in ms)

import ubx
import struct
import calendar
import os
import gobject
import logging
import sys
import socket
import time

loop = gobject.MainLoop()
lastStateTransitionTime = None

def callback(ty, packet):
    global lastStateTransitionTime
    # print("callback %s" % repr([ty, packet]))
    if ty == "ACK-ACK":
        print('\nPower mode successfully set!')
        loop.quit()
    else:
        elapsed = time.time() - lastStateTransitionTime
        if elapsed > 1:
            print('\n*** Power mode setting request not acknowledged!')
            import sys; sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', '-d', default=None)
    parser.add_argument('--mode', '-m', choices=ubx.powerSetupValueDict.keys(), default='fullPower')
    parser.add_argument('--period', '-p', default=None, help='Position update period and search period in seconds - only used in interval mode')
    parser.add_argument('--onTime', '-o', default=None, help='Duration of the ON phase in seconds, must be smaller than the period - only used in interval mode')
    args = parser.parse_args()

    mode = ubx.powerSetupValueDict[args.mode]
    if args.period is None:
        if args.mode == 'interval':
            print('Defaulting to the recommended period of 10s')
            args.period = 10
        else:
            args.period = 0
    else:
        if args.mode != 'interval':
            raise ValueError('The period parameter may be set only if the interval mode is specified!')
        try:
            args.period = int(args.period)
        except ValueError:
            raise ValueError('The period must be an integer value')
        if args.period < 5:
            raise ValueError('The period must be 5 or greater!')
        if args.period > (2**16 - 1):
            raise ValueError('The period cannot be greater than 65535 seconds!')

    if args.onTime is None:
        if args.mode == 'interval':
            print('Defaulting to an onTime of 5s')
            args.onTime = 5
        else:
            args.onTime = 0
    else:
        if args.mode != 'interval':
            raise ValueError('The onTime parameter may be set only if the interval mode is specified!')
        try:
            args.onTime = int(args.onTime)
        except ValueError:
            raise ValueError('The onTime must be an integer value')
        if args.onTime >= args.period:
            raise ValueError('The onTime must be less than the period!')
        if args.onTime > (2**16 - 1):
            raise ValueError('The onTime cannot be greater than 65535 seconds!')
    
    logging.basicConfig(level=logging.ERROR)

    if args.device is not None:
        t = ubx.Parser(callback, device=args.device)
    else:
        t = ubx.Parser(callback)
    t.send("CFG-PMS", 8, {'Version': 0, 'PowerSetupValue': mode, 'Period': args.period, 'OnTime': args.onTime})
    lastStateTransitionTime = time.time()
    loop.run()
