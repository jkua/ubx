#!/usr/bin/env python3

# Get AssistNow Online data
# Valid for 2-4 hours
# Size: 1-3 KB
# Improves TTFF to 3 seconds (typical)

# curl https://online-live1.services.u-blox.com/GetOnlineData.ashx?token=kdIs4xBnwEivvK3aQJtY9g;gnss=gps,glo;datatype=eph,alm,aux;

# AssistNow Online servers:
# https://online-live1.services.u-blox.com
# https://online-live2.services.u-blox.com

# Token (Mapper - John Kua): kdIs4xBnwEivvK3aQJtY9g

import requests
import datetime
import os

validGnss = ['gps', 'qzss', 'glo', 'bds', 'gal']
validDatatypes = ['eph', 'alm', 'aux', 'pos']

def getOnlineData(hostUrl, token, gnss=['gps', 'glo'], datatypes=['eph', 'alm', 'aux']):
    for g in gnss:
        if g not in validGnss:
            raise ValueError('{} is not a valid GNSS! Must be one of {}'.format(g, validGnss))
    for d in datatypes:
        if d not in validDatatypes:
            raise ValueError('{} is not a valid datatype! Must be one of {}'.format(d, validDatatypes))


    url = hostUrl
    url += '/GetOnlineData.ashx?'
    url += 'token={};'.format(token)
    url += 'datatype={};'.format(','.join(datatypes))
    url += 'format=mga;'
    url += 'gnss={};'.format(','.join(gnss))
    response = requests.get(url)

    if not response.ok:
        raise Exception('Failed to get data from {}'.format(hostUrl))

    return response.content


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', '-d', default=None)
    parser.add_argument('--hostUrl', '-H', default='https://online-live1.services.u-blox.com')
    parser.add_argument('--token', '-t', default='kdIs4xBnwEivvK3aQJtY9g')
    parser.add_argument('--outputPath', '-o', default='.', help='Output path')
    args = parser.parse_args()

    print('\nQuerying for AssistNow Online data...')
    downloadDt = datetime.datetime.utcnow()
    data = getOnlineData(args.hostUrl, token='kdIs4xBnwEivvK3aQJtY9g')
    print('\nReceived {} bytes.'.format(len(data)))

    outputFileName = os.path.join(args.outputPath, 'assistNowOnline_{}.bin'.format(downloadDt.strftime('%Y%m%dT%H%M%SZ')))
    print('\nSaving to {}'.format(outputFileName))

    with open(outputFileName, 'wb') as f:
        f.write(data)

    print('\nDone.')
    