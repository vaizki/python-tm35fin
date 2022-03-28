
import math

from tm35fin import Coordinates


def xy_within_1m(p1, p2):
    return all([ abs(int(p1[i])-int(p2[i])) < 2 for i in (0,1) ])

def wgs84_close_enough(p1, p2):
    # For lat, 0.00001 deg = 1.11m
    # For lon, we scale first
    def check_lat(p1, p2):
        return abs(p1[0]-p2[0])*111111 < 2
    def check_lon(p1, p2):
        lon_f = math.cos((p2[1]/180*math.pi))
        return abs(p1[1]-p2[1])*lon_f*111111 < 2
    return all((check_lat(p1,p2), check_lon(p1,p2)))


HELSINKI_XY = (385784,6672298)
HELSINKI_WGS84 = (60.17156012073224, 24.941409012372404)
    
def test_xy_to_wgs84():
    c = Coordinates(*HELSINKI_XY)
    w = c.wgs84
    assert(wgs84_close_enough(w, HELSINKI_WGS84))

def test_wgs84_to_xy():
    c = Coordinates.from_wgs84(*HELSINKI_WGS84)
    assert(xy_within_1m((c.x, c.y), HELSINKI_XY))

    
