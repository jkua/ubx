#!/usr/bin/env python3
import time
import datetime
import calendar

leapSecondsLastChanged = datetime.datetime(2016, 12, 31)
leapSecondsLastChecked = datetime.datetime(2019, 2, 22)
TAIMinusUTC = 37 # Last changed Dec 2016, last checked Feb 2019
GPSMinusUTC = TAIMinusUTC - 19 

def posixToGps(posixTimestamp, leapSeconds=18):
    gpsOffset = (datetime.datetime(1980, 1, 6) - datetime.datetime(1970, 1, 1)).total_seconds()
    gpsTimestamp = posixTimestamp - gpsOffset + leapSeconds
    return gpsTimestamp

def gpsToPosix(gpsTimestamp, leapSeconds=18):
    gpsOffset = (datetime.datetime(1980, 1, 6) - datetime.datetime(1970, 1, 1)).total_seconds()
    posixTimestamp = gpsTimestamp + gpsOffset - leapSeconds
    return posixTimestamp

def gpsWeekAndTow(gpsTimestamp):
    gpsWeekNumber = int(gpsTimestamp) // (3600 * 24 * 7)
    gpsWeekNumberRollover = gpsWeekNumber % 1024
    gpsTow = gpsTimestamp % (3600 * 24 * 7)
    return gpsWeekNumber, gpsWeekNumberRollover, gpsTow

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('year', type=int)
    parser.add_argument('month', type=int)
    parser.add_argument('day', type=int)
    parser.add_argument('hour', type=int)
    parser.add_argument('minute', type=int)
    parser.add_argument('second', type=int)
    parser.add_argument('--leapSeconds', type=int, default=None)
    args = parser.parse_args()

    curDateTime = datetime.datetime(args.year, args.month, args.day, args.hour, args.second)

    if args.leapSeconds is None:
        if curDateTime < leapSecondsLastChanged:
            raise ValueError('Specified UTC datetime is before the last leap second change on {}'.format(leapSecondsLastChanged.strftime('%Y-%m-%d')))
        if curDateTime > leapSecondsLastChecked:
            print('*** WARNING ***: Specified UTC datetime is after the last time the leap second count was checked on {}!'.format(leapSecondsLastChecked.strftime('%Y-%m-%d')))
        args.leapSeconds = GPSMinusUTC

    posixTimestamp = calendar.timegm(curDateTime.timetuple())
    gpsTimestamp = posixToGps(posixTimestamp, leapSeconds=args.leapSeconds)
    gpsWeekNumber, gpsWeekNumberRollover, gpsTow = gpsWeekAndTow(gpsTimestamp)
    posixTimestamp2 = gpsToPosix(gpsTimestamp, args.leapSeconds)

    print('\nUTC:      {}'.format(curDateTime.strftime('%Y-%m-%d %H:%M:%S')))
    print('POSIX:    {:.3f}'.format(posixTimestamp))
    print('GPS:      {:.3f}'.format(gpsTimestamp))
    print('GPS Week: {} ({})'.format(gpsWeekNumber, gpsWeekNumberRollover))
    print('GPS TOW:  {:.3f}'.format(gpsTow))
    print('POSIX 2:  {:.3f}'.format(posixTimestamp2))
    print('')
    print('GPS-UTC leap second count: {}'.format(args.leapSeconds))
    print('POSIX-GPS: {:.0f}'.format(posixTimestamp-gpsTimestamp))
    assert posixTimestamp == posixTimestamp2, 'POSIX->GPS->POSIX conversion failed! Results do not match!'
