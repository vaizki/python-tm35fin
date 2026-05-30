"""Public tuple-compatible value types."""

from __future__ import annotations

from typing import NamedTuple


class Point(NamedTuple):
    """TM35FIN / EPSG:3067 point as easting/northing meters."""

    x: float
    y: float


class Size(NamedTuple):
    """Tile size as width/height meters."""

    width: float
    height: float


class BBox(NamedTuple):
    """TM35FIN / EPSG:3067 bounding box."""

    lower_left: Point
    upper_right: Point

    @property
    def left(self) -> float:
        return self.lower_left.x

    @property
    def bottom(self) -> float:
        return self.lower_left.y

    @property
    def right(self) -> float:
        return self.upper_right.x

    @property
    def top(self) -> float:
        return self.upper_right.y

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.top - self.bottom

    @property
    def center(self) -> Point:
        return Point(self.left + self.width / 2, self.bottom + self.height / 2)


class WGS84Point(NamedTuple):
    """WGS84 point as latitude/longitude decimal degrees."""

    lat: float
    lon: float


class WGS84BBox(NamedTuple):
    """WGS84 bounding box."""

    south_west: WGS84Point
    north_east: WGS84Point

    @property
    def south(self) -> float:
        return self.south_west.lat

    @property
    def west(self) -> float:
        return self.south_west.lon

    @property
    def north(self) -> float:
        return self.north_east.lat

    @property
    def east(self) -> float:
        return self.north_east.lon
