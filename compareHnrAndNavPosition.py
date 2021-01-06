#!/usr/bin/env python3

import pickle
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Proj, transform
import math
import datetime

def determineUtmZone(longitude):
    zone = (math.floor((longitude + 180)/6) % 60) + 1
    return zone


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    args = parser.parse_args()

    data = pickle.load(open(args.input, 'rb'))

    navData = {'ITOW': [], 'LAT': [], 'LON': [], 'HEIGHT': [], 'FixType': [], 'DateTime': []}
    hnrData = {'ITOW': [], 'LAT': [], 'LON': [], 'HEIGHT': [], 'GPSFix': [], 'DateTime': []}
    
    for msg in data['NAV-PVT']:
        dt = datetime.datetime(msg[0]['Year'], msg[0]['Month'], msg[0]['Day'], msg[0]['Hour'], msg[0]['Min'], msg[0]['Sec']) + datetime.timedelta(microseconds=msg[0]['Nano']/1000.)
        for key in navData.keys():
            if key == 'DateTime':
                navData['DateTime'].append(dt)
            else:
                navData[key].append(msg[0][key])

    navItowSet = set(navData['ITOW'])

    fullHnrDt = []
    fullHnrItow = []
    fullHnrLat = []
    fullHnrLon = []
    fullHnrHeight = []
    for msg in data['HNR-PVT']:
        dt = datetime.datetime(msg[0]['Year'], msg[0]['Month'], msg[0]['Day'], msg[0]['Hour'], msg[0]['Min'], msg[0]['Sec']) + datetime.timedelta(microseconds=msg[0]['Nano']/1000.)
        fullHnrDt.append(dt)
        fullHnrItow.append(msg[0]['ITOW'])
        fullHnrLat.append(msg[0]['LAT'])
        fullHnrLon.append(msg[0]['LON'])
        fullHnrHeight.append(msg[0]['HEIGHT'])
        if msg[0]['ITOW'] not in navItowSet:
            continue
        for key in hnrData.keys():
            if key == 'DateTime':
                hnrData['DateTime'].append(dt)
            else:
                hnrData[key].append(msg[0][key])   

    itow, idxNav, idxHnr = np.intersect1d(navData['ITOW'], hnrData['ITOW'], return_indices=True)

    for key in navData.keys():
        navData[key] = np.array(navData[key])[idxNav]

    for key in hnrData.keys():
        hnrData[key] = np.array(hnrData[key])

    
    zone = determineUtmZone(navData['LON'].mean())
    projectionLatLong = Proj(proj='latlong', datum='WGS84')
    projectionUtm = Proj(proj='utm', zone=zone, datum='WGS84')
    
    fullHnrUtmE, fullHnrUtmN  = transform(projectionLatLong, projectionUtm, np.array(fullHnrLon)/1e7, np.array(fullHnrLat)/1e7) 
    navData['UTM_E'], navData['UTM_N']  = transform(projectionLatLong, projectionUtm, navData['LON']/1e7, navData['LAT']/1e7)
    hnrData['UTM_E'], hnrData['UTM_N']  = transform(projectionLatLong, projectionUtm, hnrData['LON']/1e7, hnrData['LAT']/1e7)

    dEasting = hnrData['UTM_E'] - navData['UTM_E']
    dNorthing = hnrData['UTM_N'] - navData['UTM_N']
    diff = np.sqrt(dEasting**2 + dNorthing**2)

    print('dEasting -  Mean: {:.3f} m, Std: {:.3f} m, Min: {:.3f} m, Max: {:.3f} m'.format(dEasting.mean(), dEasting.std(), dEasting.min(), dEasting.max()))
    print('dNorthing - Mean: {:.3f} m, Std: {:.3f} m, Min: {:.3f} m, Max: {:.3f} m'.format(dNorthing.mean(), dNorthing.std(), dNorthing.min(), dNorthing.max()))
    print('diff -      Mean: {:.3f} m, Std: {:.3f} m, Min: {:.3f} m, Max: {:.3f} m'.format(diff.mean(), diff.std(), diff.min(), diff.max()))

    fig, ax = plt.subplots(3, sharex=True)
    ax[0].plot(itow, dEasting)
    ax[0].set_ylabel('dEasting (m)')

    ax[1].plot(itow, dNorthing)
    ax[1].set_ylabel('dNorthing (m)')

    ax[2].plot(itow, diff)
    ax[2].plot(itow, hnrData['GPSFix'], 'r')
    ax[2].set_ylabel('diff (m)')
    ax[2].set_xlabel('ITOW')

    fig, ax = plt.subplots(4, sharex=True)
    ax[0].plot(fullHnrItow, fullHnrUtmE, 'b')
    ax[0].plot(itow, navData['UTM_E'], 'rx')
    ax[0].set_ylabel('Easting (m)')

    ax[1].plot(fullHnrItow, fullHnrUtmN, 'b')
    ax[1].plot(itow, navData['UTM_N'], 'rx')
    ax[1].set_ylabel('Northing (m)')

    ax[2].plot(fullHnrItow, fullHnrHeight, 'b')
    ax[2].plot(itow, navData['HEIGHT'], 'rx')
    ax[2].set_ylabel('Height (m)')
    ax[2].set_xlabel('ITOW')

    fig, ax = plt.subplots(1)
    ax.plot(fullHnrUtmE, fullHnrUtmN, 'b')
    ax.plot(navData['UTM_E'], navData['UTM_N'], 'rx')
    ax.set_xlabel('Easting (m)')
    ax.set_ylabel('Northing (m)')
    ax.set_aspect('equal')

    fig, ax = plt.subplots(1)
    ax.plot(fullHnrDt, fullHnrItow, 'b')
    ax.plot(navData['DateTime'], navData['ITOW'], 'rx')

    deltas = hnrData['DateTime'] - navData['DateTime']
    dSec = np.array([d.total_seconds() for d in deltas])
    print('dUTC - Mean: {:.6f} s, Std: {:.6f} s, Min: {:.6f} s, Max: {:.6f} s'.format(dSec.mean(), dSec.std(), dSec.min(), dSec.max()))
    
    fig, ax = plt.subplots(1)
    ax.plot(itow, dSec)
    ax.set_xlabel('ITOW')
    ax.set_ylabel('dUTC (s)')

    
    plt.show()
