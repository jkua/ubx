#!/usr/bin/env python3

# Get AssistNow Offline data
# Valid for up to 35 days
# Updated daily
# Size: approx 125 KB (GPS+GLO 28 days)
# Improves TTFF to 5-20 seconds (typical)

# curl http://offline-live1.services.u-blox.com/GetOfflineData.ashx?token=XXXXXXXXX;gnss=gps;period=1;resolution=1

# AssistNow Offline servers:
# https://offline-live1.services.u-blox.com
# https://offline-live2.services.u-blox.com

# Token (Mapper - John Kua): kdIs4xBnwEivvK3aQJtY9g

import requests

validGnss = ['gps', 'glo']
validDatatypes = ['eph', 'alm', 'aux', 'pos']
validPeriods = list(range(1, 6))
validResolutions = list(range(1, 4))
validDays = [1, 2, 3, 5, 7, 10, 14]
validAlmanacs = ['gps', 'qzss', 'glo', 'bds', 'gal']


def getOfflineData(hostUrl, token, gnss=['gps', 'glo'], period=4, resolution=1, days=14, almanacs=['gps','glo']):
    for g in gnss:
        if g not in validGnss:
            raise ValueError('{} is not a valid GNSS! Must be one of {}'.format(g, validGnss))
    if period not in validPeriods:
        raise ValueError('{} is not a valid period! Must be one of {}'.format(period, validPeriods))
    if resolution not in validResolutions:
        raise ValueError('{} is not a valid resolution! Must be one of {}'.format(resolution, validResolutions))
    if days not in validDays:
        raise ValueError('{} is not a valid number of days! Must be one of {}'.format(days, validDays))
    for alm in almanacs:
        if alm not in validAlmanacs:
            raise ValueError('{} is not a valid almanac! Must be one of {}'.format(alm, validAlmanacs))

    url = hostUrl
    url += '/GetOfflineData.ashx?'
    url += 'token={};'.format(token)
    url += 'gnss={};'.format(','.join(gnss))
    url += 'format=mga;'
    url += 'period={};'.format(period)
    url += 'resolution={};'.format(resolution)
    url += 'days={};'.format(days)
    url += 'almanac={};'.format(','.join(almanacs))
    response = requests.get(url)

    if not response.ok:
        raise Exception('Failed to get data from {}'.format(hostUrl))

    return response.content

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--hostUrl', '-H', default='https://offline-live1.services.u-blox.com')
    parser.add_argument('--token', '-t', default='kdIs4xBnwEivvK3aQJtY9g')
    args = parser.parse_args()

    response = getOfflineData(args.hostUrl, token='kdIs4xBnwEivvK3aQJtY9g')
    print('Received ({}):\n{}'.format(len(response), response))
