"""TM35FIN map sheet tile math."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

from .grids import (
    MAX_LEVEL,
    MIN_LEVEL,
    ORIGIN,
    SUBDIVISION_GRIDS,
    TILE_SIZES,
    TM35_COLUMNS,
    TM35_ROWS,
)
from .types import BBox, Point, Size, WGS84BBox, WGS84Point


def _clean_number(value: float) -> float | int:
    if float(value).is_integer():
        return int(value)
    return value


def _clean_point(point: Point) -> Point:
    return Point(_clean_number(point[0]), _clean_number(point[1]))


def _clean_bbox(bbox: BBox) -> BBox:
    return BBox(_clean_point(bbox[0]), _clean_point(bbox[1]))


def validate_level(level: int) -> int:
    if not isinstance(level, int):
        raise ValueError("Tile level must be an integer")
    if level < MIN_LEVEL or level > MAX_LEVEL:
        raise ValueError(f"Tile level must be in the range {MIN_LEVEL}-{MAX_LEVEL}")
    return level


def validate_tile_name(name: str) -> str:
    if not isinstance(name, str):
        raise ValueError("Tile name must be a string")

    name = name.strip().upper()
    if len(name) < 2 or len(name) > MAX_LEVEL + 1:
        raise ValueError(f"Invalid TM35FIN tile name: {name!r}")

    row = name[0]
    if row not in TM35_ROWS:
        raise ValueError(f"Invalid TM35FIN row letter in tile name: {name!r}")

    try:
        column = int(name[1])
    except ValueError as exc:
        raise ValueError(f"Invalid TM35FIN column in tile name: {name!r}") from exc
    if column not in TM35_COLUMNS:
        raise ValueError(f"Invalid TM35FIN column in tile name: {name!r}")

    for offset, symbol in enumerate(name[2:]):
        grid = SUBDIVISION_GRIDS[offset]
        if not grid.contains(symbol):
            raise ValueError(f"Invalid TM35FIN child tile symbol in tile name: {name!r}")

    return name


def tile_level(name: str) -> int:
    return len(validate_tile_name(name)) - 1


def point_to_tile_name(x: float, y: float, level: int = MAX_LEVEL) -> str:
    validate_level(level)
    if x is None or y is None:
        raise ValueError("Both x and y are required")

    x_offset = float(x) - ORIGIN[0]
    y_offset = float(y) - ORIGIN[1]
    if x_offset < 0 or y_offset < 0:
        raise ValueError("Coordinates are outside the supported TM35FIN sheet area")

    width, height = TILE_SIZES[0]
    x_index = math.floor(x_offset / width)
    y_index = math.floor(y_offset / height)
    if y_index < 0 or y_index >= len(TM35_ROWS) or x_index not in TM35_COLUMNS:
        raise ValueError("Coordinates are outside the supported TM35FIN sheet area")

    parts = [f"{TM35_ROWS[y_index]}{x_index}"]
    x_offset %= width
    y_offset %= height

    for child_level in range(2, level + 1):
        width, height = TILE_SIZES[child_level - 1]
        grid = SUBDIVISION_GRIDS[child_level - 2]
        child_x = math.floor(x_offset / width)
        child_y = math.floor(y_offset / height)
        if child_x < 0 or child_x >= grid.width or child_y < 0 or child_y >= grid.height:
            raise ValueError("Coordinates are outside the supported TM35FIN sheet area")
        parts.append(grid.symbol_for(child_x, child_y))
        x_offset %= width
        y_offset %= height

    return "".join(parts)


def tile_name_to_bbox(name: str) -> BBox:
    name = validate_tile_name(name)
    level = len(name) - 1

    row_index = TM35_ROWS.index(name[0])
    column = int(name[1])
    x = ORIGIN[0] + column * TILE_SIZES[0][0]
    y = ORIGIN[1] + row_index * TILE_SIZES[0][1]

    for offset, symbol in enumerate(name[2:]):
        grid = SUBDIVISION_GRIDS[offset]
        x_index, y_index = grid.index_for(symbol)
        width, height = TILE_SIZES[offset + 1]
        x += x_index * width
        y += y_index * height

    width, height = TILE_SIZES[level - 1]
    return _clean_bbox(BBox(Point(x, y), Point(x + width, y + height)))


def point_in_bbox(point: Point, bbox: BBox) -> bool:
    (left, bottom), (right, top) = bbox
    x, y = point
    return left <= x < right and bottom <= y < top


@dataclass(frozen=True)
class MapTile:
    """ETRS-TM35FIN map sheet tile."""

    _name: str

    TILE_SIZES = TILE_SIZES
    TILE_LEVELS = MAX_LEVEL
    TM35_ROWS = TM35_ROWS

    def __init__(self, name: str | None = None, x: float | None = None, y: float | None = None, level: int | None = None):
        if name is not None:
            if x is not None or y is not None:
                raise ValueError("Supply only name or x/y")
            normalized = validate_tile_name(name)
            inferred_level = len(normalized) - 1
            if level is not None and validate_level(level) != inferred_level:
                raise ValueError("Match level with name or omit it")
            object.__setattr__(self, "_name", normalized)
            return

        if x is None or y is None:
            raise ValueError("Supply both x and y or name")
        if level is None:
            level = MAX_LEVEL
        validate_level(level)
        object.__setattr__(self, "_name", point_to_tile_name(x, y, level=level))

    @classmethod
    def from_name(cls, name: str) -> "MapTile":
        return cls(name=name)

    @classmethod
    def from_point(cls, x: float, y: float, level: int = MAX_LEVEL) -> "MapTile":
        return cls(x=x, y=y, level=level)

    @classmethod
    def from_wgs84(cls, lat: float, lon: float, level: int = MAX_LEVEL) -> "MapTile":
        from .crs import wgs84_to_tm35fin

        x, y = wgs84_to_tm35fin(lat, lon)
        return cls.from_point(x, y, level=level)

    @classmethod
    def tiles_for_wgs84_bbox(
        cls,
        south: float,
        west: float,
        north: float,
        east: float,
        level: int = MAX_LEVEL,
    ) -> list["MapTile"]:
        from .crs import wgs84_to_tm35fin

        validate_level(level)
        corners = (
            wgs84_to_tm35fin(south, west),
            wgs84_to_tm35fin(south, east),
            wgs84_to_tm35fin(north, west),
            wgs84_to_tm35fin(north, east),
        )
        xs = [point[0] for point in corners]
        ys = [point[1] for point in corners]
        width, height = TILE_SIZES[level - 1]
        start_x = math.floor((min(xs) - ORIGIN[0]) / width) * width + ORIGIN[0]
        end_x = math.floor((max(xs) - ORIGIN[0]) / width) * width + ORIGIN[0]
        start_y = math.floor((min(ys) - ORIGIN[1]) / height) * height + ORIGIN[1]
        end_y = math.floor((max(ys) - ORIGIN[1]) / height) * height + ORIGIN[1]

        tiles: list[MapTile] = []
        current_y = start_y
        while current_y <= end_y:
            current_x = start_x
            while current_x <= end_x:
                try:
                    tiles.append(cls.from_point(current_x, current_y, level=level))
                except ValueError:
                    pass
                current_x += width
            current_y += height
        return sorted(set(tiles), key=lambda tile: tile.name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def level(self) -> int:
        return len(self.name) - 1

    @property
    def size(self) -> Size:
        width, height = _clean_point(Point(*TILE_SIZES[self.level - 1]))
        return Size(width, height)

    @property
    def bbox(self) -> BBox:
        return tile_name_to_bbox(self.name)

    @property
    def bounding_box(self):
        from .coordinates import Coordinates

        lower_left, upper_right = self.bbox
        return Coordinates(*lower_left), Coordinates(*upper_right)

    @property
    def tm35fin_bbox(self) -> BBox:
        return self.bbox

    @property
    def wgs84_bbox(self) -> WGS84BBox:
        from .crs import tm35fin_to_wgs84

        (left, bottom), (right, top) = self.bbox
        sw = WGS84Point(*tm35fin_to_wgs84(left, bottom))
        ne = WGS84Point(*tm35fin_to_wgs84(right, top))
        return WGS84BBox(sw, ne)

    @property
    def center(self):
        from .coordinates import Coordinates

        (left, bottom), (right, top) = self.bbox
        return Coordinates((left + right) / 2, (bottom + top) / 2)

    def contains(self, point) -> bool:
        if isinstance(point, tuple):
            x, y = point
        else:
            x, y = point.x, point.y
        return point_in_bbox((x, y), self.bbox)

    def __contains__(self, point) -> bool:
        return self.contains(point)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


def unique_tiles(tiles: Iterable[MapTile]) -> list[MapTile]:
    return sorted(set(tiles), key=lambda tile: tile.name)
