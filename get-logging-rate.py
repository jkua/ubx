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


# Get logging rate (in ms)

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
    if ty == "CFG-RATE":
        timeRefDictInv = dict( [(v,k) for k, v in ubx.timeRefDict.items()] )
        timeRef = timeRefDictInv[packet[0]['Time']].upper()
        print('    Measurement rate: {} ms'.format(packet[0]['Meas']))
        print('    Navigation rate: {} measurements'.format(packet[0]['Nav']))
        print('    Time reference: {} '.format(timeRef))
        loop.quit()
    else:
        elapsed = time.time() - lastStateTransitionTime
        if elapsed > 1:
            print('\n*** Did not receive CFG-RATE message before timeout!')
            import sys; sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', '-d', default=None)
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.ERROR)

    if args.device is not None:
        t = ubx.Parser(callback, device=args.device)
    else:
        t = ubx.Parser(callback)
    print('Polling for CFG-RATE - navigation/measurement rate settings...')
    t.send("CFG-RATE", 0, [])
    lastStateTransitionTime = time.time()
    loop.run()
