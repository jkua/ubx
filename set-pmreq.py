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

import logging
import sys
import ubx

logger = logging.getLogger(__name__)

def callback(ty, packet):
    logger.info("callback %s" % repr([ty, packet]))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('duration', help='Wakeup after N seconds - 0 for infinite', type=float, default=0.0)
    parser.add_argument('--flags', '-f', metavar='BITS', choices=[0,2,4,6], help='Task flags - 0=none, 2=backup, 4=force, 6=backup+force', type=int, default=0)
    parser.add_argument('--wakeupSources', '-w', metavar='BITS', help='Sources of wakeup (bitmask) - 0 for none, 8=uartrx, 32=extint0, 64=extint1, 128=spics', type=int, default=0)
    parser.add_argument('--device', '-d', help='Specify the serial port device to communicate with. e.g. /dev/ttyO5')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    cmd = {}
    length = 8
    cmd['duration'] = int(args.duration*1e3)
    cmd['flags'] = args.flags
    if args.flags & 4 or not args.wakeupSources==0:
        cmd['version'] = 0
        cmd['wakeupSources'] = args.wakeupSources
        length = 16
    logger.info('RXM-PMREQ, {}, {}'.format(length, cmd))
    t = ubx.Parser(callback, device=args.device)
    t.send("RXM-PMREQ", length, cmd)
