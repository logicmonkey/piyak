import math
from math import pi, sin, cos, radians, sqrt, degrees, asin

def generate_track(curve, location):
    # ------------------------------------------------------------------------------
    # haversine returns the distance between two points {latitude, longitude}
    def haversine(p, q):

        dlat = radians(q['lat'] - p['lat'])
        dlon = radians(q['lon'] - p['lon'])
        lat1 = radians(p['lat'])
        lat2 = radians(q['lat'])

        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        c = 2*asin(sqrt(a))

        return c * R * 1000 # return value in metres

    # ------------------------------------------------------------------------------
    # geometry in the xy plane - here are some nice curves
    def geometry(t, c):
        if c == 'circle':
            x = r*cos(t)
            y = r*sin(t)
        if c == 'bernoulli':
            x = r*sqrt(2)*cos(t)/(sin(t)*sin(t)+1)
            y = r*sqrt(2)*cos(t)*sin(t)/(sin(t)*sin(t)+1)
        if c == 'gerono':
            x = r*cos(t)
            y = r*cos(t)*sin(t)
        return (x, y)

    # ------------------------------------------------------------------------------
    # xy to geographical coordinates
    def geographical(p, l):
        x, y = p

        if l == 'oxenhope':
            o = {'lat':  53.8100160, 'lon':   -1.9596520}
        if l == 'waikiki':
            o = {'lat':  21.2765000, 'lon': -157.8460000}
        if l == 'capetown':
            o = {'lat': -34.2452585, 'lon':   18.6372443}

        # world coordinates R in km -> x,y in km, {lat, lon} in degrees
        lat = o['lat'] + degrees(y/R)
        lon = o['lon'] + degrees(x/(R*cos(radians(o['lat']))))

        return {'lat': lat, 'lon': lon, 'x': 200.0 + 200.0 * x, 'y': 150.0 + 200.0 * y}

    # ------------------------------------------------------------------------------
    # generate_track
    R        = 6371                  # earth radius in km
    r        = 1.00                  # radius used in xy geometry
    TRACKRES = 500
    dtheta   = 2*pi/TRACKRES         # assuming curves have 2*pi periodicity
    theta    = 0
    track    = []
    dist     = 0
    q        = {}

    for step in range(TRACKRES):
        # calculate xy coordinates and map to geographical.
        # R in km and geometry x,y in km {lat, lon} in degrees
        p = geographical(geometry(theta, curve), location)

        if theta > 0: # calculate distance to last point
            dist += haversine(p, q)

        track.append({'lat': p['lat'], 'lon': p['lon'], 'dist': dist, 'x': p['x'], 'y': p['y']})
        theta += dtheta
        q = p

    # close the loop to the first point from the last for full lap distance
    track_length = dist + haversine(q, geographical(geometry(0, curve), location))

    return track, track_length
