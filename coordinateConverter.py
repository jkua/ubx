import math

from pyproj import Proj, transform

class CoordinateConverter(object):
    def __init__(self, zone=None):
        self.zone = None
        self.datumIn = 'WGS84'
        self.datumOut = 'WGS84'
        self.projectionLatLong = Proj(proj='latlong', datum=self.datumIn)
        self.setUtmProjection(zone)

    def convertLLToUtm(self, lat, lon):
        if self.projectionUtm is None:
            zone = self.determineUtmZone(lon)
            self.setUtmProjection(zone)

        x, y = transform(self.projectionLatLong, self.projectionUtm, lon, lat)
        return x, y, self.zone

    def convertUtmToLL(self, x, y, zone=None):
        if zone:
            self.setUtmProjection(zone)

        lon, lat = transform(self.projectionUtm, self.projectionLatLong, x, y)
        return lat, lon

    def setUtmProjection(self, zone=None):
        if zone:
            self.zone = zone
        if self.zone:
            self.projectionUtm = Proj(proj='utm', zone=self.zone, datum=self.datumOut)
        else:
            self.projectionUtm = None

    @staticmethod
    def determineUtmZone(longitude):
        zone = (math.floor((longitude + 180)/6) % 60) + 1
        return zone
