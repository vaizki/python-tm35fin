"""Coordinate convenience object for TM35FIN tile lookups."""

from __future__ import annotations

from dataclasses import dataclass

from .crs import tm35fin_to_wgs84, wgs84_to_tm35fin


def _clean_number(value: float) -> float | int:
    if float(value).is_integer():
        return int(value)
    return value


@dataclass(frozen=True)
class Coordinates:
    """ETRS-TM35FIN coordinate pair, stored as x/y in meters."""

    x: float
    y: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "x", _clean_number(float(self.x)))
        object.__setattr__(self, "y", _clean_number(float(self.y)))

    def get_tile(self, level: int = 6):
        from .tiles import MapTile

        return MapTile.from_point(self.x, self.y, level=level)

    @property
    def tile(self):
        return self.get_tile()

    @property
    def wgs84(self) -> tuple[float, float]:
        return tm35fin_to_wgs84(self.x, self.y)

    @classmethod
    def from_wgs84(cls, lat: float, lon: float) -> "Coordinates":
        x, y = wgs84_to_tm35fin(lat, lon)
        return cls(x, y)

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.x},{self.y})"

