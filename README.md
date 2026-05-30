# TM35FIN map tile helpers for Python

`tm35fin` converts between points and Finnish TM35FIN map sheet names
(`karttalehdet`). The core tile math is pure Python and dependency-free.

The public API is designed for the common case where callers have WGS84
latitude/longitude points or bounding boxes, while the internal tile grid is
kept as deterministic EPSG:3067 / ETRS-TM35FIN meter math.

Official tile index reference:
[Maanmittauslaitos UTM-lehtijako PDF](https://www.maanmittauslaitos.fi/sites/maanmittauslaitos.fi/files/old/UTM_lehtijakopdf.pdf).

## Installation

```bash
pip install tm35fin
```

For development:

```bash
python -m pip install ".[dev]"
```

To run CRS reference tests against `pyproj`:

```bash
python -m pip install ".[reference]"
```

## Examples

```python
from tm35fin import Coordinates, MapTile

# Helsinki railway station, ETRS-TM35FIN / EPSG:3067
c = Coordinates(385784, 6672298)
c.tile.name
# "L4133B3"

c.get_tile(level=3).name
# "L413"

MapTile("L413").bounding_box
# (Coordinates(356000,6666000), Coordinates(404000,6690000))

MapTile("L413").bbox.lower_left.x
# 356000

MapTile("L413").bbox.width
# 48000

MapTile("L413").size
# Size(width=48000, height=24000)

MapTile("L413").center
# Coordinates(380000,6678000)

c in MapTile("L413")
# True
```

WGS84-first helpers:

```python
tile = MapTile.from_wgs84(60.17156012073224, 24.941409012372404)
tile.name
# "L4133B3"

tile.wgs84_bbox
# WGS84BBox(south_west=WGS84Point(lat=...), north_east=WGS84Point(lat=...))
```

Low-level pure functions are also available:

```python
from tm35fin import point_to_tile_name, tile_name_to_bbox

point_to_tile_name(385784, 6672298, level=6)
# "L4133B3"

tile_name_to_bbox("L4133B3")
# ((383000, 6672000), (386000, 6675000))
```

## API Reference

See [API.md](API.md) for the full API reference, including constructors,
function signatures, return types, containment rules, CRS helpers, constants,
and compatibility notes.

## Semantics

Coordinates are stored as floats. Tile lookup uses the actual numeric point and
does not truncate coordinates in `Coordinates.__init__`.

Containment uses half-open bounds:

```python
left <= x < right and bottom <= y < top
```

That means a point exactly on a shared upper or right tile edge belongs only to
the adjacent tile, not both.

The built-in WGS84 conversion is pure Python and narrowly scoped to
WGS84/ETRS89 latitude-longitude and EPSG:3067 ETRS-TM35FIN. It is intended for
Finland and the immediately surrounding area covered by the TM35FIN sheet
system.

The package ships `py.typed`, so downstream type checkers can use the inline
type hints.

## Known Limitations

- Official half tiles such as `V3113R` are not implemented yet.
- Official non-rectangular sheet existence is not fully encoded yet; the
  current validator enforces the supported TM35FIN row/column naming range and
  child symbols.
- This is not a general GIS or CRS library. Use a GIS library for arbitrary CRS
  transformations, geodesic distances, or topology.

## Development

```bash
python -m pip install ".[dev]"
python -m pytest
```

Run optional `pyproj` reference tests:

```bash
python -m pip install ".[reference]"
python -m pytest
```

Build a PyPI artifact:

```bash
python -m pip install ".[dev]"
python -m build
twine check dist/*
```
