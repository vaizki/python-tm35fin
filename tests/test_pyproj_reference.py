import pytest

from tm35fin.crs import tm35fin_to_wgs84, wgs84_to_tm35fin


pyproj = pytest.importorskip("pyproj")


REFERENCE_POINTS = [
    pytest.param(60.17156012073224, 24.941409012372404, id="helsinki"),
    pytest.param(69.9086, 27.0284, id="utsjoki"),
    pytest.param(69.0603, 20.5486, id="kilpisjarvi"),
    pytest.param(60.0973, 19.9348, id="mariehamn"),
    pytest.param(62.6010, 29.7636, id="joensuu"),
    pytest.param(65.0121, 25.4651, id="oulu"),
]


@pytest.fixture(scope="module")
def to_tm35fin():
    return pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3067", always_xy=True)


@pytest.fixture(scope="module")
def to_wgs84():
    return pyproj.Transformer.from_crs("EPSG:3067", "EPSG:4326", always_xy=True)


@pytest.mark.parametrize(("lat", "lon"), REFERENCE_POINTS)
def test_wgs84_to_tm35fin_matches_pyproj(to_tm35fin, lat, lon):
    expected_x, expected_y = to_tm35fin.transform(lon, lat)
    actual_x, actual_y = wgs84_to_tm35fin(lat, lon)

    assert actual_x == pytest.approx(expected_x, abs=0.02)
    assert actual_y == pytest.approx(expected_y, abs=0.02)


@pytest.mark.parametrize(("lat", "lon"), REFERENCE_POINTS)
def test_tm35fin_to_wgs84_matches_pyproj(to_tm35fin, to_wgs84, lat, lon):
    x, y = to_tm35fin.transform(lon, lat)
    expected_lon, expected_lat = to_wgs84.transform(x, y)
    actual_lat, actual_lon = tm35fin_to_wgs84(x, y)

    assert actual_lat == pytest.approx(expected_lat, abs=2e-8)
    assert actual_lon == pytest.approx(expected_lon, abs=2e-8)
