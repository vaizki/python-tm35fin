
from tm35fin import Coordinates, MapTile

HELSINKI_XY = (385784,6672298)
HELSINKI_TILE6 = 'L4133B3'
HEL_C = Coordinates(*HELSINKI_XY)

MAX_LVL = 6

def test_helxy_tile():
    t = HEL_C.tile
    assert(t.name == HELSINKI_TILE6)

    
def test_tile_names():
    for i in range(1,MAX_LVL+1):
        assert(HEL_C.get_tile(level=i).name == HELSINKI_TILE6[:i+1])

def test_xy_in_tile():
    # Check that Helsinki point is in L4..L4133B3 
    for i in range(1,MAX_LVL+1):
        assert(HEL_C in MapTile(HELSINKI_TILE6[:i+1]))

def test_tile_bb():
    bb = MapTile('L413').bounding_box
    assert(bb == (Coordinates(356000,6666000), Coordinates(404000,6690000)))

def test_tile_center():
    assert(MapTile('L413').center == Coordinates(380000,6678000))

def test_tile_level():
    for i in range(1, MAX_LVL+1):
        assert(MapTile(HELSINKI_TILE6[:i+1]).level == i)

        
