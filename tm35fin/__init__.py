"""

    ETRS-TM35FIN coordinate system helpers

    2022 Jukka Väisänen (@vaizki)
    Rewrote & relicensed under MIT license

    WGS84 coordinate conversions (c) 2012-2015,2022 Olli Lammi (olammi@iki.fi)

    Original math with numpy & proj
    2012-2014 Lauri Kangas (@lkangas)
    Original License: ICCLEIYSIUYA (http://evvk.com/evvktvh.html)

"""

# pylint: disable=invalid-name

from __future__ import annotations
from typing import Union, Optional, Tuple

from .coordinates import ETRSTM35FINxy_to_WGS84lalo, WGS84lalo_to_ETRSTM35FINxy



class Coordinates:
    """
        ETRS-TM35FIN coordinate object (x,y)
    """
    def __init__(self, x: int, y: int):
        self.x = int(x)
        self.y = int(y)
        self._tile = None

    def get_tile(self, level: int = 6) -> MapTile:
        """
            Get a MapTile object where this point resides
        """
        return MapTile(x=self.x, y=self.y, level=level)

    @property
    def tile(self) -> MapTile:
        """
            Smallest tile where this point is.
            Use get_tile() to get a bigger tile.
        """
        if not self._tile:
            self._tile = self.get_tile()
        return self._tile

    @property
    def wgs84(self) -> Tuple(int,int):
        """
            These coordinates in WGS84 system (GPS devices etc)
        """
        ll = ETRSTM35FINxy_to_WGS84lalo({ 'N': self.y, 'E': self.x })
        return ll['La'], ll['Lo']

    @classmethod
    def from_wgs84(cls, lat, lon):
        xy = WGS84lalo_to_ETRSTM35FINxy({ 'La': lat, 'Lo': lon})
        return cls(xy['E'],xy['N'])

    def __repr__(self):
        return f'{self.__class__.__name__}({self.x},{self.y})'

    def __eq__(self, other):

        if isinstance(other, self.__class__):
            ox = other.x
            oy = other.y
        elif isinstance(other, tuple) and len(other) == 2:
            ox,oy = other
        else:
            return False
        return (self.x, self.y) == (ox, oy)



class MapTile:
    """
        ETRS-TM35FIN map tile (karttalehti) object (x,y)
    """
    TILE_SIZES = [ (192000, 96000), # 1:200k
                   (96000, 48000),  # 1:100k
                   (48000, 24000),  # 1:50k
                   (24000, 12000),  # 1:25k
                   (6000, 6000),    # 1:10k
                   (3000, 3000) ]   # 1:5k
    TILE_LEVELS = 6

    # TM35 top-level tiles have a latter+number designation
    TM35_ROWS = ['K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X']

    # Mapping subtiles x,y to number for all levels except 1:25k
    GRID_4 = (('1','2'),('3','4'))

    # Mapping for subtiles of 1:25k
    GRID_8 = (('A','B'), ('C','D'),('E','F'),('G','H'))

    # Tile K4 lower right is spec'd as (500000,6570000)
    # K0 lower left is (500000-5*192000, 6570000) and our math reference
    K0_LLPOS = (-460000, 6570000)

    def __init__(self, name=None, x=None, y=None, level=None):
        if name:
            if x or y:
                raise ValueError('Supply only name or x/y')
            lvl = self._name_to_level(name)
            if level and lvl != level:
                raise ValueError('Match level with name or omit it')
            level = lvl
        else:
            if not (x and y):
                raise ValueError('Supply both x and y or name')
            if not level:
                level = self.TILE_LEVELS
        if level < 1 or level > self.TILE_LEVELS:
            raise ValueError('Tile level must be in the range 1-6')
        self._level = level
        self._name = name
        self._px = x
        self._py = y
        self._poff = None
        self._bb = None

    def __str__(self):
        return self.name

    def __repr__(self):
        # Ensure we have a calculated name
        n = self.name
        if self._poff:
            return f'{self.__class__.__name__}({n}+<{self._poff[0]},{self._poff[1]}>m)'
        return f'{self.__class__.__name__}({n})'

    @property
    def level(self):
        return self._level

    @property
    def size(self):
        return self.TILE_SIZES[self.level-1]

    @property
    def name(self):
        if not self._name:
            self._resolve_name()
        return self._name

    def _resolve_name(self):
        tile_name=''
        xd = self._px - self.K0_LLPOS[0]
        yd = self._py - self.K0_LLPOS[1]
        for lvl in range(self._level):
            txs, tys = self.TILE_SIZES[lvl]
            xtile, xd = divmod(xd, txs)
            ytile, yd = divmod(yd, tys)
            grid = self.GRID_4
            if lvl == 0:
                tile_name += f'{self.TM35_ROWS[ytile]}{xtile}'
            else:
                if lvl == 4:
                    grid = self.GRID_8
                tile_name += f'{grid[xtile][ytile]}'
        self._name = tile_name
        self._update_bb(x1=xtile, y1=ytile)
        self._poff = (xd, yd)

    def _name_is_legal(self, name: str):
        if len(name) < 2 or len(name) > 7:
            return False
        legal = ['KLMNPQRSTUVWX', '23456', '1234', '1234', '1234', 'ABCDEFGH', '1234']
        for i,c in enumerate(name):
            if not c in legal[i]:
                return False
        return True

    def _name_to_level(self, name: str):
        if not self._name_is_legal(name):
            return -1
        return len(name)-1

    def __contains__(self, point: Union[Coordinates,tuple]):
        """
            Check if a Coordinate is on this tile
        """
        if isinstance(point, tuple):
            x,y = point
        if isinstance(point, Coordinates):
            x,y = point.x, point.y
        if not self._bb:
            self._update_bb()
        bb = self._bb
        if (x >= bb[0][0] and x <= bb[1][0]) and (y >= bb[0][1] and y <= bb[1][1]):
            return True
        return False


    @property
    def bounding_box(self) -> Tuple[Coordinates,Coordinates]:
        """
            Bounding box in lower-left,upper-right order
            ((x1,y1),(x2,y2))
        """
        if not self._bb:
            self._update_bb()
        bb = self._bb
        return Coordinates(*bb[0]), Coordinates(*bb[1])


    def _update_bb(self, x1=None, y1=None):
        if not (x1 and y1):
            tile = self.name
            x1, y1 = self.K0_LLPOS
            x1 += int(tile[1]) * self.TILE_SIZES[0][0]
            y1 += self.TM35_ROWS.index(tile[0]) * self.TILE_SIZES[0][1]
            size = self.TILE_SIZES
            if len(tile) > 2:
                if tile[2] in '34R':
                    x1 += size[1][0]
                if tile[2] in '24':
                    y1 += size[1][1]
            if len(tile) > 3:
                if tile[3] in '34R':
                    x1 += size[2][0]
                if tile[3] in '24':
                    y1 += size[2][1]
            if len(tile) > 4:
                if tile[4] in '34R':
                    x1 += size[3][0]
                if tile[4] in '24':
                    y1 += size[3][1]
            if len(tile) > 5:
                offset = 0
                if tile[5] in 'CD':
                    offset = 1
                if tile[5] in 'EFR':
                    offset = 2
                if tile[5] in 'GH':
                    offset = 3
                x1 += size[4][0]*offset
                if tile[5] in 'BDFH':
                    y1 += size[4][1]
            if len(tile) == 7:
                if tile[6] in '34':
                    x1 += size[5][0]
                if tile[6] in '24':
                    y1 += size[5][1]
        ts = self.size
        self._bb = ((x1,y1),(x1+ts[0],y1+ts[1]))


    @property
    def center(self) -> Coordinates:
        """
            Coordinate() of tile center point
        """
        bb = self.bounding_box
        sz = self.size
        return Coordinates(int(bb[0].x + sz[0]/2),
                           int(bb[0].y + sz[1]/2))
