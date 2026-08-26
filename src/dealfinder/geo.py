from math import radians, sin, cos, sqrt, atan2

EARTH_RADIUS_MILES = 3958.7613

def distance_miles(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None
    p1, p2 = radians(lat1), radians(lat2)
    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(p1)*cos(p2)*sin(dlon/2)**2
    return EARTH_RADIUS_MILES * 2 * atan2(sqrt(a), sqrt(1-a))
