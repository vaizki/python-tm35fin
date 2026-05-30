"""Small WGS84 <-> ETRS-TM35FIN conversion layer.

The default backend is pure Python and implements only the narrow EPSG:4326
latitude/longitude to EPSG:3067 ETRS-TM35FIN use case needed by this package.
"""

from __future__ import annotations

import math


CENTRAL_MERIDIAN = 27.0
FALSE_EASTING = 500000.0
SCALE = 0.9996

GRS80_A = 6378137.0
GRS80_F = 1.0 / 298.257222101


def _ellipsoid_parameters(a: float = GRS80_A, f: float = GRS80_F, k0: float = SCALE) -> dict[str, float]:
    n = f / (2.0 - f)
    return {
        "a": a,
        "f": f,
        "k0": k0,
        "e": math.sqrt(2.0 * f - f**2),
        "a1": a / (1.0 + n) * (1.0 + n**2 / 4.0 + n**4 / 64.0),
        "h1": 1.0 / 2.0 * n - 2.0 / 3.0 * n**2 + 37.0 / 96.0 * n**3 - 1.0 / 360.0 * n**4,
        "h2": 1.0 / 48.0 * n**2 + 1.0 / 15.0 * n**3 - 437.0 / 1440.0 * n**4,
        "h3": 17.0 / 480.0 * n**3 - 37.0 / 840.0 * n**4,
        "h4": 4397.0 / 161280.0 * n**4,
        "h1p": 1.0 / 2.0 * n - 2.0 / 3.0 * n**2 + 5.0 / 16.0 * n**3 + 41.0 / 180.0 * n**4,
        "h2p": 13.0 / 48.0 * n**2 - 3.0 / 5.0 * n**3 + 557.0 / 1440.0 * n**4,
        "h3p": 61.0 / 240.0 * n**3 - 103.0 / 140.0 * n**4,
        "h4p": 49561.0 / 161280.0 * n**4,
    }


_GRS80 = _ellipsoid_parameters()


def _atanh(value: float) -> float:
    return math.log((1.0 + value) / (1.0 - value)) / 2.0


def wgs84_to_tm35fin(lat: float, lon: float) -> tuple[float, float]:
    """Convert WGS84/ETRS89 latitude and longitude to EPSG:3067 x/y."""

    ellipsoid = _GRS80
    lo0 = math.radians(CENTRAL_MERIDIAN)
    la = math.radians(lat)
    lo = math.radians(lon)

    e = ellipsoid["e"]
    q = math.asinh(math.tan(la)) - e * _atanh(e * math.sin(la))
    beta = math.atan(math.sinh(q))
    eta_p = _atanh(math.cos(beta) * math.sin(lo - lo0))
    xi_p = math.asin(math.sin(beta) * math.cosh(eta_p))

    xi = (
        xi_p
        + ellipsoid["h1p"] * math.sin(2.0 * xi_p) * math.cosh(2.0 * eta_p)
        + ellipsoid["h2p"] * math.sin(4.0 * xi_p) * math.cosh(4.0 * eta_p)
        + ellipsoid["h3p"] * math.sin(6.0 * xi_p) * math.cosh(6.0 * eta_p)
        + ellipsoid["h4p"] * math.sin(8.0 * xi_p) * math.cosh(8.0 * eta_p)
    )
    eta = (
        eta_p
        + ellipsoid["h1p"] * math.cos(2.0 * xi_p) * math.sinh(2.0 * eta_p)
        + ellipsoid["h2p"] * math.cos(4.0 * xi_p) * math.sinh(4.0 * eta_p)
        + ellipsoid["h3p"] * math.cos(6.0 * xi_p) * math.sinh(6.0 * eta_p)
        + ellipsoid["h4p"] * math.cos(8.0 * xi_p) * math.sinh(8.0 * eta_p)
    )

    northing = ellipsoid["a1"] * xi * ellipsoid["k0"]
    easting = ellipsoid["a1"] * eta * ellipsoid["k0"] + FALSE_EASTING
    return easting, northing


def tm35fin_to_wgs84(x: float, y: float) -> tuple[float, float]:
    """Convert EPSG:3067 x/y to WGS84/ETRS89 latitude and longitude."""

    ellipsoid = _GRS80
    lo0 = math.radians(CENTRAL_MERIDIAN)
    xi = y / (ellipsoid["a1"] * ellipsoid["k0"])
    eta = (x - FALSE_EASTING) / (ellipsoid["a1"] * ellipsoid["k0"])

    xi_p = (
        xi
        - ellipsoid["h1"] * math.sin(2.0 * xi) * math.cosh(2.0 * eta)
        - ellipsoid["h2"] * math.sin(4.0 * xi) * math.cosh(4.0 * eta)
        - ellipsoid["h3"] * math.sin(6.0 * xi) * math.cosh(6.0 * eta)
        - ellipsoid["h4"] * math.sin(8.0 * xi) * math.cosh(8.0 * eta)
    )
    eta_p = (
        eta
        - ellipsoid["h1"] * math.cos(2.0 * xi) * math.sinh(2.0 * eta)
        - ellipsoid["h2"] * math.cos(4.0 * xi) * math.sinh(4.0 * eta)
        - ellipsoid["h3"] * math.cos(6.0 * xi) * math.sinh(6.0 * eta)
        - ellipsoid["h4"] * math.cos(8.0 * xi) * math.sinh(8.0 * eta)
    )

    beta = math.asin(math.sin(xi_p) / math.cosh(eta_p))
    q = math.asinh(math.tan(beta))
    q_p = q
    for _ in range(4):
        q_p = q + ellipsoid["e"] * _atanh(ellipsoid["e"] * math.tanh(q_p))

    lat = math.degrees(math.atan(math.sinh(q_p)))
    lon = math.degrees(lo0 + math.asin(math.tanh(eta_p) / math.cos(beta)))
    return lat, lon


def ETRSTM35FINxy_to_WGS84lalo(value: dict[str, float]) -> dict[str, float]:
    """Backward-compatible legacy dict wrapper."""

    lat, lon = tm35fin_to_wgs84(value["E"], value["N"])
    return {"La": lat, "Lo": lon}


def WGS84lalo_to_ETRSTM35FINxy(value: dict[str, float]) -> dict[str, float]:
    """Backward-compatible legacy dict wrapper."""

    x, y = wgs84_to_tm35fin(value["La"], value["Lo"])
    return {"E": x, "N": y}

