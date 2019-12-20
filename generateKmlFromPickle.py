#!/usr/bin/env python3

from mapper.kml import resampleTrack, writeKmlTrack
import matplotlib.pyplot as plt
import os
import numpy as np
import pickle
import datetime
import calendar

if __name__=='__main__':
    import json
    import numpy as np
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('--plot', '-p', action='store_true', help='Show plots')
    parser.add_argument('--kml', '-k', help='Filename for KML generation')
    parser.add_argument('--resample', '-r', type=int, help='Resample points - 0 for no resample.')
    parser.add_argument('--nav', '-n', action='store_true', help='Use NAV-PVT instead of HNR-PVT')
    args = parser.parse_args()

    data = pickle.load(open(args.input, 'rb'), encoding='latin1')
    timestamps = []
    latitude = []
    longitude = []

    navMessageType = 'NAV-PVT' if args.nav else 'HNR-PVT'

    for packet in data[navMessageType]:
        # timestamp = packet[0]['ITOW']/1e3
        year = packet[0]['Year']
        month = packet[0]['Month']
        day = packet[0]['Day']
        hour = packet[0]['Hour']
        minute = packet[0]['Min']
        second = packet[0]['Sec']
        nano = packet[0]['Nano']
        dt = datetime.datetime(year, month, day, hour, minute, second) + datetime.timedelta(microseconds=nano/1000)
        timestamp = calendar.timegm(dt.timetuple())


        lat = packet[0]['LAT']/1e7
        lon = packet[0]['LON']/1e7
        # alt = packet[0]['HEIGHT']/1e3
        # heading = packet[0]['HeadVeh']/1e5
        # speed = packet[0]['Speed']/1e3
        # fix = fixTypeDict[packet[0]['GPSFix']]
        
        timestamps.append(timestamp)
        latitude.append(lat)
        longitude.append(lon)

    # Write KML
    if args.resample:
        timestamps_resampled, latitude_resampled, longitude_resampled = resampleTrack(timestamps, latitude, longitude, args.resample)
    else:
        timestamps_resampled = timestamps
        latitude_resampled = latitude
        longitude_resampled = longitude
        
    if args.kml:
        kmlFilename = args.kml
    else:
        kmlFilename = os.path.splitext(args.input)[0] + '.kml'
    writeKmlTrack(timestamps_resampled, latitude_resampled, longitude_resampled, kmlFilename)