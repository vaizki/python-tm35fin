import math

from tm35fin import Coordinates, MapTile, WGS84BBox, WGS84Point
from tm35fin.crs import tm35fin_to_wgs84, wgs84_to_tm35fin


HELSINKI_XY = (385784, 6672298)
HELSINKI_WGS84 = (60.17156012073224, 24.941409012372404)


def xy_within_1m(p1, p2):
    return all(abs(p1[i] - p2[i]) < 2 for i in (0, 1))


def wgs84_close_enough(p1, p2):
    # For lat, 0.00001 deg = 1.11m. For lon, scale at this latitude.
    def check_lat(p1, p2):
        return abs(p1[0] - p2[0]) * 111111 < 2

    def check_lon(p1, p2):
        lon_f = math.cos((p2[1] / 180 * math.pi))
        return abs(p1[1] - p2[1]) * lon_f * 111111 < 2

    return all((check_lat(p1, p2), check_lon(p1, p2)))


def test_coordinates_store_float_precision():
    c = Coordinates(385784.25, 6672298.75)

    assert c.x == 385784.25
    assert c.y == 6672298.75


def test_xy_to_wgs84_compatibility():
    c = Coordinates(*HELSINKI_XY)

    assert wgs84_close_enough(c.wgs84, HELSINKI_WGS84)
    assert wgs84_close_enough(tm35fin_to_wgs84(*HELSINKI_XY), HELSINKI_WGS84)


def test_wgs84_to_xy_compatibility():
    c = Coordinates.from_wgs84(*HELSINKI_WGS84)

    assert xy_within_1m((c.x, c.y), HELSINKI_XY)
    assert xy_within_1m(wgs84_to_tm35fin(*HELSINKI_WGS84), HELSINKI_XY)


def test_wgs84_first_tile_constructor():
    tile = MapTile.from_wgs84(*HELSINKI_WGS84, level=6)

    assert tile.name == "L4133B3"


def test_tile_wgs84_bbox_contains_original_wgs84_point():
    tile = MapTile.from_wgs84(*HELSINKI_WGS84, level=6)
    bbox = tile.wgs84_bbox
    assert isinstance(bbox, WGS84BBox)
    assert isinstance(bbox.south_west, WGS84Point)

    (south, west), (north, east) = bbox
    lat, lon = HELSINKI_WGS84

    assert south <= lat < north
    assert west <= lon < east


def test_wgs84_bbox_supports_named_access():
    bbox = MapTile("L4133B3").wgs84_bbox

    assert bbox.south_west.lat < bbox.north_east.lat
    assert bbox.south_west.lon < bbox.north_east.lon
    assert bbox.south == bbox.south_west.lat
    assert bbox.west == bbox.south_west.lon
    assert bbox.north == bbox.north_east.lat
    assert bbox.east == bbox.north_east.lon
