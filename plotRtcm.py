#!/usr/bin/env python3

# plotRtcm.py

import os
import pickle
import matplotlib.pyplot as plt
from pyproj import Proj, transform
import numpy as np
import datetime

def determineUtmZone(longitude):
    zone = (np.floor((longitude + 180)/6) % 60) + 1
    return zone

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    args = parser.parse_args()

    inputPath = os.path.split(args.input)[0]

    data = pickle.load(open(args.input, 'rb'), encoding='latin1')

    rtcmTimeTypes = {}
    rtcmTypeCount = {}
    messageTypes = set()

    distanceToBaseStation = []
    startPosition = 37.785889, -122.271341
    zone = determineUtmZone(startPosition[1])
    projectionLatLong = Proj(proj='latlong', datum='WGS84')
    projectionUtm = Proj(proj='utm', zone=zone, datum='WGS84')
    startUtm  = transform(projectionLatLong, projectionUtm, startPosition[1], startPosition[0]) 
    
    dts = []
    carrierPhaseSolutionStatus = []
    for msg in data['NAV-PVT']:
        year = msg[0]['Year']
        month = msg[0]['Month']
        day = msg[0]['Day']
        hour = msg[0]['Hour']
        minute = msg[0]['Min']
        second = msg[0]['Sec']
        nano = msg[0]['Nano']
        dt = datetime.datetime(year, month, day, hour, minute, second) + datetime.timedelta(microseconds=nano/1000.)
        dts.append(dt)

        rtcmTimeTypes[dt] = []

        lat = msg[0]['LAT']/1e7
        lon = msg[0]['LON']/1e7
        curUtm  = transform(projectionLatLong, projectionUtm, lon, lat) 
        dist = np.sqrt((curUtm[0] - startUtm[0])**2 + (curUtm[1] - startUtm[1])**2)
        distanceToBaseStation.append(dist)
        
        carrSoln = msg[0]['Flags'] >> 6
        carrierPhaseSolutionStatus.append(carrSoln)

    for msg in data['RXM-RTCM']:
        dt = msg[0]['lastPvtDt']
        msgType = msg[0]['MsgType']
        if dt is None:
            continue

        rtcmTimeTypes[dt].append(msgType)
        messageTypes.add(msgType)

    for messageType in messageTypes:
        rtcmTypeCount[messageType] = [0] * len(dts)
    numMessagesPerTime = [0] * len(dts)

    for i, dt in enumerate(dts):
        numMessagesPerTime[i] = len(rtcmTimeTypes[dt])
        for msgType in rtcmTimeTypes[dt]:
            rtcmTypeCount[msgType][i] += 1

    fig, axes = plt.subplots(len(rtcmTypeCount) + 1, sharex=True)
    axes[0].plot(dts, numMessagesPerTime)
    axes[0].set_ylabel('Total')

    for msgType, ax in zip(sorted(rtcmTypeCount.keys()), axes[1:]):
        ax.plot(dts, rtcmTypeCount[msgType])
        ax.set_ylabel(str(msgType))

    axes[-1].set_xlabel('Time')

    fig.tight_layout()
    fig.savefig(os.path.join(inputPath, 'rtcmMessagesReceived.png'), dpi=200)


    fig, axes = plt.subplots(3, sharex=True)
    axes[0].plot(dts, carrierPhaseSolutionStatus)
    axes[0].set_ylabel('Solution Status')

    axes[1].plot(dts, numMessagesPerTime)
    axes[1].set_ylabel('Messages')

    axes[2].plot(dts, distanceToBaseStation)
    axes[2].set_ylabel('Distance')

    axes[0].set_title('RTK solution status vs. RTCM message reception')

    fig.tight_layout()
    fig.savefig(os.path.join(inputPath, 'rtkSolutionVsRtcmMessages.png'), dpi=200)

    plt.show()
