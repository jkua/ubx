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
        print('\nHigh Nav Rate successfully set!')
        loop.quit()
    elif ty == "ACK-NACK":
        print('\n*** High Nav Rate setting NACKed - not understood!')
        import sys; sys.exit(1)
    else:
        elapsed = time.time() - lastStateTransitionTime
        if elapsed > 1:
            print('\n*** High Nav Rate setting request not acknowledged!')
            import sys; sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', '-d', default=None)
    parser.add_argument('rate', default=1, type=int)
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.DEBUG)

    assert args.rate >= 0 and args.rate <= 30
    if args.device is not None:
        t = ubx.Parser(callback, device=args.device)
    else:
        t = ubx.Parser(callback)
    t.send("CFG-HNR", 4, {'HighNavRate': args.rate})
    lastStateTransitionTime = time.time()
    loop.run()
