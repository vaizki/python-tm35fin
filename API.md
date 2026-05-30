# API Reference

This document describes the public API for `tm35fin` v2.

The package is tile-first internally: all TM35FIN sheet names are resolved in
the EPSG:3067 / ETRS-TM35FIN meter grid. The public API also includes WGS84
helpers because most callers start from latitude/longitude points or bounding
boxes.

## Coordinate Order

The library uses two coordinate orders:

- TM35FIN / EPSG:3067 coordinates are always `(x, y)` where `x` is easting and
  `y` is northing, in meters.
- WGS84 coordinates are always `(lat, lon)` where latitude and longitude are in
  decimal degrees.

Bounding boxes are represented as lower-left and upper-right point pairs:

```python
((left, bottom), (right, top))
```

For WGS84 bounding boxes, the same shape is returned as:

```python
((south, west), (north, east))
```

## Main Imports

```python
from tm35fin import (
    Coordinates,
    MapTile,
    point_to_tile_name,
    tile_name_to_bbox,
    validate_tile_name,
)
```

The package root also exports tuple-compatible value types and the legacy CRS
wrapper functions:

```python
from tm35fin import BBox, Point, Size, WGS84BBox, WGS84Point
```

```python
from tm35fin import ETRSTM35FINxy_to_WGS84lalo, WGS84lalo_to_ETRSTM35FINxy
```

## `Coordinates`

```python
Coordinates(x: float, y: float)
```

An immutable ETRS-TM35FIN coordinate pair stored as `x` and `y` in meters.
Values are preserved as floats; whole-number floats are displayed as integers.

```python
from tm35fin import Coordinates

c = Coordinates(385784, 6672298)
c.x
# 385784
c.y
# 6672298
```

### `Coordinates.get_tile()`

```python
Coordinates.get_tile(level: int = 6) -> MapTile
```

Returns the tile containing this point at the requested tile level.

```python
c = Coordinates(385784, 6672298)
c.get_tile(level=3).name
# "L413"
```

Raises `ValueError` if `level` is outside `1..6` or the point is outside the
supported TM35FIN sheet grid.

### `Coordinates.tile`

```python
Coordinates.tile -> MapTile
```

Shortcut for `get_tile(level=6)`.

```python
Coordinates(385784, 6672298).tile.name
# "L4133B3"
```

### `Coordinates.wgs84`

```python
Coordinates.wgs84 -> tuple[float, float]
```

Returns `(lat, lon)` in WGS84 / ETRS89 decimal degrees.

```python
Coordinates(385784, 6672298).wgs84
# (60.17156012073224, 24.941409012372404)
```

### `Coordinates.from_wgs84()`

```python
Coordinates.from_wgs84(lat: float, lon: float) -> Coordinates
```

Converts WGS84 latitude/longitude to ETRS-TM35FIN coordinates.

```python
c = Coordinates.from_wgs84(60.17156012073224, 24.941409012372404)
round(c.x), round(c.y)
# (385784, 6672298)
```

### Iteration And Equality

`Coordinates` is a frozen dataclass. Equality compares `Coordinates` objects by
their `x` and `y` fields.

It is also iterable:

```python
x, y = Coordinates(385784, 6672298)
```

## `MapTile`

```python
MapTile(name: str | None = None, x: float | None = None, y: float | None = None, level: int | None = None)
```

Represents one TM35FIN map sheet tile.

Construct from a tile name:

```python
tile = MapTile("L4133B3")
tile.name
# "L4133B3"
```

Construct from a TM35FIN point:

```python
tile = MapTile(x=385784, y=6672298, level=6)
tile.name
# "L4133B3"
```

When constructing from a point, `level` defaults to `6`. When constructing from
a name, the level is inferred from the name. Supplying both a name and x/y
raises `ValueError`.

### `MapTile.from_name()`

```python
MapTile.from_name(name: str) -> MapTile
```

Explicit constructor for a TM35FIN tile name.

```python
MapTile.from_name("L413").level
# 3
```

### `MapTile.from_point()`

```python
MapTile.from_point(x: float, y: float, level: int = 6) -> MapTile
```

Explicit constructor for an ETRS-TM35FIN point.

```python
MapTile.from_point(385784, 6672298, level=6).name
# "L4133B3"
```

### `MapTile.from_wgs84()`

```python
MapTile.from_wgs84(lat: float, lon: float, level: int = 6) -> MapTile
```

Converts a WGS84 latitude/longitude point to ETRS-TM35FIN, then returns the tile
containing that point.

```python
MapTile.from_wgs84(60.17156012073224, 24.941409012372404).name
# "L4133B3"
```

### `MapTile.tiles_for_wgs84_bbox()`

```python
MapTile.tiles_for_wgs84_bbox(
    south: float,
    west: float,
    north: float,
    east: float,
    level: int = 6,
) -> list[MapTile]
```

Returns all TM35FIN tiles intersecting the WGS84 bounding box approximation.
The four WGS84 corners are projected into TM35FIN, then the covering rectangular
tile range is enumerated.

```python
tiles = MapTile.tiles_for_wgs84_bbox(
    south=60.16,
    west=24.90,
    north=60.18,
    east=24.96,
    level=6,
)
[tile.name for tile in tiles]
```

The returned list is sorted by tile name and duplicate tiles are removed.
Coordinates outside the supported sheet grid are skipped while enumerating the
covering range.

### `MapTile.name`

```python
MapTile.name -> str
```

The normalized uppercase TM35FIN tile name.

```python
MapTile("l413").name
# "L413"
```

### `MapTile.level`

```python
MapTile.level -> int
```

Tile level from `1` to `6`.

```python
MapTile("L4133B3").level
# 6
```

### `MapTile.size`

```python
MapTile.size -> Size
```

Tile width and height in meters.

```python
MapTile("L413").size
# Size(width=48000, height=24000)
```

### `MapTile.bbox`

```python
MapTile.bbox -> BBox
```

Returns the TM35FIN bounding box as a tuple-compatible `BBox`.

```python
bbox = MapTile("L4133B3").bbox
bbox.lower_left.x
# 383000

bbox.width
# 3000

bbox.center
# Point(x=384500, y=6673500)

(left, bottom), (right, top) = bbox
# tuple unpacking still works
```

### `MapTile.bounding_box`

```python
MapTile.bounding_box -> tuple[Coordinates, Coordinates]
```

Compatibility property returning the TM35FIN bounding box as `Coordinates`
objects.

```python
MapTile("L413").bounding_box
# (Coordinates(356000,6666000), Coordinates(404000,6690000))
```

### `MapTile.tm35fin_bbox`

```python
MapTile.tm35fin_bbox -> BBox
```

Alias for `MapTile.bbox`.

### `MapTile.wgs84_bbox`

```python
MapTile.wgs84_bbox -> WGS84BBox
```

Returns the WGS84 bounding box as a tuple-compatible `WGS84BBox`.

```python
bbox = MapTile("L4133B3").wgs84_bbox
bbox.south_west.lat
bbox.south

(south, west), (north, east) = bbox
# tuple unpacking still works
```

The conversion projects only the lower-left and upper-right TM35FIN corners.
For small TM35FIN sheet tiles this is normally what callers want, but it is not
a general geospatial polygon transformation.

### `MapTile.center`

```python
MapTile.center -> Coordinates
```

Returns the center point of the tile in TM35FIN coordinates.

```python
MapTile("L413").center
# Coordinates(380000,6678000)
```

### `MapTile.contains()`

```python
MapTile.contains(point: Coordinates | tuple[float, float]) -> bool
```

Returns whether a TM35FIN point is inside the tile.

```python
tile = MapTile("L413")
tile.contains(Coordinates(385784, 6672298))
# True
tile.contains((385784, 6672298))
# True
```

Containment uses half-open bounds:

```python
left <= x < right and bottom <= y < top
```

This prevents a point exactly on a shared upper or right edge from belonging to
two adjacent tiles.

### `point in MapTile`

```python
Coordinates(385784, 6672298) in MapTile("L413")
# True
```

Equivalent to `MapTile.contains(point)`.

### String Representation

```python
str(MapTile("L413"))
# "L413"

repr(MapTile("L413"))
# "MapTile(L413)"
```

## Tile Functions

### `point_to_tile_name()`

```python
point_to_tile_name(x: float, y: float, level: int = 6) -> str
```

Returns the TM35FIN tile name containing an ETRS-TM35FIN point.

```python
from tm35fin import point_to_tile_name

point_to_tile_name(385784, 6672298, level=6)
# "L4133B3"
```

Raises `ValueError` for invalid levels, missing coordinates, or coordinates
outside the supported sheet grid.

### `tile_name_to_bbox()`

```python
tile_name_to_bbox(name: str) -> BBox
```

Decodes a TM35FIN tile name into its TM35FIN bounding box.

```python
from tm35fin import tile_name_to_bbox

tile_name_to_bbox("L413")
# BBox(lower_left=Point(x=356000, y=6666000), upper_right=Point(x=404000, y=6690000))
```

Raises `ValueError` if the tile name is invalid.

### `validate_tile_name()`

```python
validate_tile_name(name: str) -> str
```

Normalizes and validates a TM35FIN tile name. Returns the stripped uppercase
name.

```python
from tm35fin import validate_tile_name

validate_tile_name(" l413 ")
# "L413"
```

Raises `ValueError` if the name is not a supported TM35FIN sheet name.

### `tile_level()`

```python
from tm35fin.tiles import tile_level

tile_level(name: str) -> int
```

Returns the level implied by a valid tile name.

```python
tile_level("L4133B3")
# 6
```

This function is available from `tm35fin.tiles`, but is not exported from the
package root.

### `point_in_bbox()`

```python
from tm35fin.tiles import point_in_bbox

point_in_bbox(
    point: tuple[float, float],
    bbox: tuple[tuple[float, float], tuple[float, float]],
) -> bool
```

Checks whether a point is inside a half-open bounding box.

### `unique_tiles()`

```python
from tm35fin.tiles import unique_tiles

unique_tiles(tiles: Iterable[MapTile]) -> list[MapTile]
```

Returns unique tiles sorted by tile name.

## Value Types

The public value types live in `tm35fin.types` and are exported from the package
root. They are `NamedTuple` classes, so they support both attribute access and
normal tuple unpacking.

### `Point`

```python
Point(x: float, y: float)
```

TM35FIN / EPSG:3067 point in easting/northing meters.

```python
from tm35fin import Point

p = Point(385784, 6672298)
p.x
# 385784
x, y = p
```

### `Size`

```python
Size(width: float, height: float)
```

Tile size in meters.

```python
from tm35fin import Size

size = Size(48000, 24000)
size.width
# 48000
width, height = size
```

### `BBox`

```python
BBox(lower_left: Point, upper_right: Point)
```

TM35FIN bounding box.

```python
from tm35fin import BBox, Point

bbox = BBox(Point(383000, 6672000), Point(386000, 6675000))
bbox.upper_right.y
# 6675000

bbox.left
# 383000
bbox.bottom
# 6672000
bbox.right
# 386000
bbox.top
# 6675000
bbox.width
# 3000
bbox.height
# 3000
bbox.center
# Point(x=384500, y=6673500)
```

### `WGS84Point`

```python
WGS84Point(lat: float, lon: float)
```

WGS84 point in decimal degrees.

### `WGS84BBox`

```python
WGS84BBox(south_west: WGS84Point, north_east: WGS84Point)
```

WGS84 bounding box.

Convenience properties:

```python
bbox.south
bbox.west
bbox.north
bbox.east
```

## CRS Functions

The CRS layer is pure Python and narrowly scoped to WGS84/ETRS89
latitude-longitude and EPSG:3067 / ETRS-TM35FIN.

The package has no runtime CRS dependency. Optional reference tests compare the
pure Python implementation against `pyproj`:

```bash
python -m pip install ".[reference]"
python -m pytest
```

### `wgs84_to_tm35fin()`

```python
from tm35fin.crs import wgs84_to_tm35fin

wgs84_to_tm35fin(lat: float, lon: float) -> tuple[float, float]
```

Converts WGS84 latitude/longitude to TM35FIN `(x, y)`.

```python
x, y = wgs84_to_tm35fin(60.17156012073224, 24.941409012372404)
round(x), round(y)
# (385784, 6672298)
```

### `tm35fin_to_wgs84()`

```python
from tm35fin.crs import tm35fin_to_wgs84

tm35fin_to_wgs84(x: float, y: float) -> tuple[float, float]
```

Converts TM35FIN `(x, y)` to WGS84 `(lat, lon)`.

```python
tm35fin_to_wgs84(385784, 6672298)
# (60.17156012073224, 24.941409012372404)
```

### Legacy Dict Wrappers

These functions are retained for compatibility with older code:

```python
from tm35fin import ETRSTM35FINxy_to_WGS84lalo, WGS84lalo_to_ETRSTM35FINxy

ETRSTM35FINxy_to_WGS84lalo({"E": 385784, "N": 6672298})
# {"La": 60.17156012073224, "Lo": 24.941409012372404}

WGS84lalo_to_ETRSTM35FINxy({"La": 60.17156012073224, "Lo": 24.941409012372404})
# {"E": 385784.14..., "N": 6672297.99...}
```

## Constants

Grid constants are available from `tm35fin.grids`.

```python
from tm35fin.grids import ORIGIN, TILE_SIZES, TM35_ROWS
```

### `ORIGIN`

```python
ORIGIN == (-460000.0, 6570000.0)
```

Lower-left origin for the rectangular TM35FIN sheet math.

### `TM35_ROWS`

```python
TM35_ROWS == ("K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X")
```

Supported top-level row letters.

### `TILE_SIZES`

```python
TILE_SIZES == (
    (192000.0, 96000.0),
    (96000.0, 48000.0),
    (48000.0, 24000.0),
    (24000.0, 12000.0),
    (6000.0, 6000.0),
    (3000.0, 3000.0),
)
```

Tile sizes by level.

## Tile Levels

| Level | Example | Size in meters |
| --- | --- | --- |
| 1 | `L4` | `192000 x 96000` |
| 2 | `L41` | `96000 x 48000` |
| 3 | `L413` | `48000 x 24000` |
| 4 | `L4133` | `24000 x 12000` |
| 5 | `L4133B` | `6000 x 6000` |
| 6 | `L4133B3` | `3000 x 3000` |

## Exceptions

The public API raises `ValueError` for invalid user input:

- invalid tile levels;
- invalid tile names;
- missing `x` or `y` values;
- coordinates outside the supported rectangular TM35FIN sheet grid;
- inconsistent constructor arguments, such as supplying both `name` and `x/y`.

No custom exception hierarchy is currently defined.

## Typing

The package ships a `py.typed` marker and exposes inline type hints to
downstream type checkers.

## Validity Scope

The tile system is intended for Finland and the immediately surrounding area
covered by the official TM35FIN sheet index. The current implementation
validates the rectangular row/column and child-symbol grid. It does not yet
encode every official non-rectangular sheet existence rule or half-sheet rule.

Official half tiles such as `V3113R` are not supported yet.

## Compatibility Notes

The v2 API intentionally differs from the previous implementation in these
areas:

- `Coordinates` no longer truncates x/y to integers during construction.
- Tile containment is half-open instead of inclusive on all edges.
- CRS conversion code is limited to the WGS84/ETRS89 and EPSG:3067 use case.
- Legacy KKJ, MGRS, Google Maps, distance, and bearing helpers are not part of
  the v2 public API.
