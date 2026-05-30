"""Declarative TM35FIN map sheet grid definitions."""

from __future__ import annotations

from dataclasses import dataclass


ORIGIN = (-460000.0, 6570000.0)
TM35_ROWS = tuple("KLMNPQRSTUVWX")
TM35_COLUMNS = tuple(range(2, 7))


@dataclass(frozen=True)
class SymbolGrid:
    """Mapping between child tile offsets and sheet symbols.

    Symbols are stored x-major: ``symbols[x_index][y_index]``. That keeps
    encoding and decoding symmetric and matches the TM35FIN sheet examples.
    """

    symbols: tuple[tuple[str, ...], ...]

    @property
    def width(self) -> int:
        return len(self.symbols)

    @property
    def height(self) -> int:
        return len(self.symbols[0])

    def symbol_for(self, x_index: int, y_index: int) -> str:
        if x_index < 0 or y_index < 0:
            raise IndexError("negative tile index")
        return self.symbols[x_index][y_index]

    def index_for(self, symbol: str) -> tuple[int, int]:
        for x_index, column in enumerate(self.symbols):
            for y_index, candidate in enumerate(column):
                if candidate == symbol:
                    return x_index, y_index
        raise KeyError(symbol)

    def contains(self, symbol: str) -> bool:
        try:
            self.index_for(symbol)
        except KeyError:
            return False
        return True


GRID_4 = SymbolGrid((("1", "2"), ("3", "4")))
GRID_8 = SymbolGrid((("A", "B"), ("C", "D"), ("E", "F"), ("G", "H")))


TILE_SIZES = (
    (192000.0, 96000.0),  # 1:200k
    (96000.0, 48000.0),  # 1:100k
    (48000.0, 24000.0),  # 1:50k
    (24000.0, 12000.0),  # 1:25k
    (6000.0, 6000.0),  # 1:10k
    (3000.0, 3000.0),  # 1:5k
)


SUBDIVISION_GRIDS = (
    GRID_4,
    GRID_4,
    GRID_4,
    GRID_8,
    GRID_4,
)


MIN_LEVEL = 1
MAX_LEVEL = len(TILE_SIZES)

