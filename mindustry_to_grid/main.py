from typing import Callable
from flood_types import Cell, CellType
from .parse import parse_save, SaveData


def _nothingCell_factory() -> Cell:
    return Cell(CellType.NOTHING, 0.0)


def _wallCell_factory() -> Cell:
    return Cell(CellType.WALL, 0.0)


def _generatorCell_factory() -> Cell:
    return Cell(CellType.GENERATOR, 0.0)


IDMAP: dict[int, Callable[[], Cell]] = {
    0: _nothingCell_factory,
    33: _nothingCell_factory,
    133: _nothingCell_factory,
    134: _nothingCell_factory,
    135: _nothingCell_factory,
    136: _nothingCell_factory,
    137: _nothingCell_factory,
    138: _nothingCell_factory,
    139: _nothingCell_factory,
    140: _nothingCell_factory,
    141: _nothingCell_factory,
    34: _nothingCell_factory,
    35: _nothingCell_factory,
    36: _nothingCell_factory,
    37: _nothingCell_factory,
    38: _nothingCell_factory,
    39: _nothingCell_factory,
    40: _nothingCell_factory,
    41: _nothingCell_factory,
    42: _nothingCell_factory,
    43: _nothingCell_factory,
    44: _nothingCell_factory,
    45: _nothingCell_factory,
    46: _nothingCell_factory,
    47: _nothingCell_factory,
    48: _nothingCell_factory,
    49: _nothingCell_factory,
    50: _nothingCell_factory,
    51: _nothingCell_factory,
    52: _nothingCell_factory,
    53: _nothingCell_factory,
    54: _nothingCell_factory,
    55: _nothingCell_factory,
    56: _nothingCell_factory,
    57: _nothingCell_factory,
    58: _nothingCell_factory,
    59: _nothingCell_factory,
    60: _nothingCell_factory,
    61: _nothingCell_factory,
    62: _nothingCell_factory,
    63: _nothingCell_factory,
    64: _nothingCell_factory,
    66: _nothingCell_factory,
    67: _nothingCell_factory,
    68: _nothingCell_factory,
    69: _nothingCell_factory,
    70: _nothingCell_factory,
    71: _nothingCell_factory,
    72: _nothingCell_factory,
    73: _nothingCell_factory,
    74: _nothingCell_factory,
    75: _nothingCell_factory,
    76: _nothingCell_factory,
    77: _nothingCell_factory,
    78: _nothingCell_factory,
    79: _nothingCell_factory,
    130: _nothingCell_factory,
    131: _nothingCell_factory,
    132: _nothingCell_factory,
    80: _wallCell_factory,
    81: _wallCell_factory,
    82: _wallCell_factory,
    83: _wallCell_factory,
    84: _wallCell_factory,
    85: _wallCell_factory,
    86: _wallCell_factory,
    87: _wallCell_factory,
    88: _wallCell_factory,
    89: _wallCell_factory,
    90: _wallCell_factory,
    91: _wallCell_factory,
    92: _wallCell_factory,
    93: _wallCell_factory,
    94: _wallCell_factory,
    95: _wallCell_factory,
    96: _wallCell_factory,
    97: _wallCell_factory,
    98: _wallCell_factory,
    99: _wallCell_factory,
    100: _wallCell_factory,
    101: _wallCell_factory,
    102: _wallCell_factory,
    103: _wallCell_factory,
    104: _wallCell_factory,
    124: _wallCell_factory,
    125: _wallCell_factory,
    156: _wallCell_factory,
    157: _wallCell_factory,
    158: _wallCell_factory,
    160: _wallCell_factory,
    178: _wallCell_factory,
    339: _generatorCell_factory,
    340: _generatorCell_factory,
    341: _generatorCell_factory,
    342: _generatorCell_factory,
    343: _generatorCell_factory,
    344: _generatorCell_factory,
}


def get_grid(path: str) -> list[list[Cell]]:
    parsed: SaveData = parse_save(path)
    cells: list[Cell] = []
    for tile in parsed.map.terrain:
        for _ in range(tile[2] + 3):
            cells.append(IDMAP.get(tile[0], _nothingCell_factory)())

    for block in parsed.map.blocks:
        for i in range(block.index, block.index + block.run + 1):
            cells[i] = IDMAP.get(block.block_id, _nothingCell_factory)()

    return _create_grid(parsed.map.width, parsed.map.height, cells)


def _create_grid(width: int, height: int, cells: list[Cell]) -> list[list[Cell]]:
    grid: list[list[Cell]] = []
    cellI: int = 0
    for _ in range(height):
        row: list[Cell] = []
        for _ in range(width):
            row.append(cells[cellI])
            cellI += 1
        grid.append(row)

    grid.reverse()
    grid[5][5].type = CellType.GENERATOR
    return grid
