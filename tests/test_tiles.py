import pytest

from tm35fin import BBox, Coordinates, MapTile, Point, Size
from tm35fin.tiles import point_to_tile_name, tile_name_to_bbox, validate_tile_name


HELSINKI_XY = (385784, 6672298)
HELSINKI_TILE6 = "L4133B3"
MAX_LVL = 6


def test_compatibility_point_to_tile_names_for_all_levels():
    point = Coordinates(*HELSINKI_XY)

    assert point.tile.name == HELSINKI_TILE6
    for level in range(1, MAX_LVL + 1):
        assert point.get_tile(level=level).name == HELSINKI_TILE6[: level + 1]


def test_explicit_point_to_tile_function_for_all_levels():
    x, y = HELSINKI_XY

    for level in range(1, MAX_LVL + 1):
        assert point_to_tile_name(x, y, level=level) == HELSINKI_TILE6[: level + 1]


def test_explicit_map_tile_constructors():
    assert MapTile.from_name(HELSINKI_TILE6).name == HELSINKI_TILE6
    assert MapTile.from_point(*HELSINKI_XY, level=6).name == HELSINKI_TILE6


def test_tile_name_to_bbox_for_all_levels():
    expected = {
        "L4": ((308000, 6666000), (500000, 6762000)),
        "L41": ((308000, 6666000), (404000, 6714000)),
        "L413": ((356000, 6666000), (404000, 6690000)),
        "L4133": ((380000, 6666000), (404000, 6678000)),
        "L4133B": ((380000, 6672000), (386000, 6678000)),
        "L4133B3": ((383000, 6672000), (386000, 6675000)),
    }

    for name, bbox in expected.items():
        decoded = tile_name_to_bbox(name)
        assert isinstance(decoded, BBox)
        assert isinstance(decoded.lower_left, Point)
        assert decoded == bbox
        assert MapTile(name).bounding_box == (
            Coordinates(*bbox[0]),
            Coordinates(*bbox[1]),
        )


def test_bbox_supports_named_access_and_tuple_unpacking():
    bbox = MapTile("L4133B3").bbox

    assert bbox.lower_left.x == 383000
    assert bbox.lower_left.y == 6672000
    assert bbox.upper_right.x == 386000
    assert bbox.upper_right.y == 6675000

    (left, bottom), (right, top) = bbox
    assert (left, bottom, right, top) == (383000, 6672000, 386000, 6675000)


def test_tm35fin_bbox_is_canonical_bbox_alias():
    tile = MapTile("L4133B3")

    assert tile.tm35fin_bbox == tile.bbox
    assert isinstance(tile.tm35fin_bbox, BBox)


def test_bbox_convenience_properties():
    bbox = MapTile("L4133B3").bbox

    assert bbox.left == 383000
    assert bbox.bottom == 6672000
    assert bbox.right == 386000
    assert bbox.top == 6675000
    assert bbox.width == 3000
    assert bbox.height == 3000
    assert bbox.center == Point(384500, 6673500)


def test_tile_center():
    assert MapTile("L413").center == Coordinates(380000, 6678000)


def test_tile_size_supports_named_access_and_tuple_unpacking():
    size = MapTile("L413").size

    assert isinstance(size, Size)
    assert size.width == 48000
    assert size.height == 24000
    assert size == (48000, 24000)


def test_tile_level_inferred_from_name():
    for level in range(1, MAX_LVL + 1):
        assert MapTile(HELSINKI_TILE6[: level + 1]).level == level


def test_round_trip_point_tile_bbox_contains_point():
    point = Coordinates(*HELSINKI_XY)

    for level in range(1, MAX_LVL + 1):
        tile = point.get_tile(level=level)
        assert point in tile


def test_contains_uses_half_open_bounds():
    tile = MapTile("L413")

    assert Coordinates(356000, 6666000) in tile
    assert Coordinates(403999.999, 6689999.999) in tile
    assert Coordinates(404000, 6690000) not in tile
    assert Coordinates(404000, 6678000) not in tile
    assert Coordinates(380000, 6690000) not in tile


def test_zero_coordinates_are_accepted_as_values_not_missing_arguments():
    tile = MapTile(x=0, y=6570000, level=1)

    assert tile.level == 1
    assert tile.name == "K2"


@pytest.mark.parametrize(
    "name",
    [
        "",
        "L",
        "I4",
        "L1",
        "L49",
        "L4133I",
        "L4133B9",
        "L4133B33",
    ],
)
def test_invalid_tile_names_raise_clear_value_error(name):
    with pytest.raises(ValueError):
        validate_tile_name(name)
    with pytest.raises(ValueError):
        MapTile(name)


def test_coordinates_outside_supported_grid_raise_clear_value_error():
    with pytest.raises(ValueError, match="outside"):
        point_to_tile_name(-9999999, -9999999, level=6)
