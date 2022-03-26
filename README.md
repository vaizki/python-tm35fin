# ETRS-TM35FIN coordinate system for Python 3.8+

This library provides utility classes to work with ETRS-TM35FIN coordinates and map tiles as utilized by the national government agencies of Finland.

Finnish map tiles show [here]( https://www.maanmittauslaitos.fi/sites/maanmittauslaitos.fi/files/old/TM35-lehtijako.pdf).

## Maturity level

Low. API may change. I will package this up properly with time.

This package was written mostly to convert from coordinates to TM35 Map Tiles (karttalehdet) and back. 

## Examples

```
from tm35fin import Coordinates, MapTile

# Helsinki railway station point
c = Coordinates(385784,6672298)
c.wgs84         # (60.17156012073224, 24.941409012372404)

t = c.tile
t.name          # 'L4133B3'
t.size          # (3000,3000)  = 3km x 3km    
t.bounding_box  # (Coordinates(383000,6672000), Coordinates(386000,6675000))

# In WGS84
[ p.wgs84 for p in t.bounding_box ]    #  [(60.16809771362508, 24.891441776018347), (60.19586617397734, 24.943783308698634)]

# Get a larger tile
t = c.get_tile(level=3)

# We got tile L413 and our initialization point was 29.8km E & 6.3km N of tile corner
repr(t)         # MapTile(L413+<29784,6298>m)

print(c in t)   # True, point is on the tile

# Create MapTile via name
mt = MapTile('L331')

# Get center point
mt.center       # Coordinates(236000,6678000)

```

## Known limitations

- So called "half tiles" (puolikaslehdet) designated with L & R (example: V3113R) are not supported
- There are no real geo-helpers like checking distance between points etc, convert to WGS84 (`Coordinates.wgs84`) and use another library 
- The coordinate system and library are tested only with coordinates in Finland and surrounding Baltic Sea
- I'm lazy

## Acknowledgements

- WGS84 coordinate conversions (c) 2012-2015,2022 Olli Lammi (olammi@iki.fi)
- Original tile math with numpy 2012-2014 Lauri Kangas (@lkangas)


