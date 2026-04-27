from typing import Callable
from flood_types import Cell, CellType
from .parse import parse_save, SaveData


def _nothingCell_factory() -> Cell:
    return Cell(CellType.NOTHING, 0.0)


IDMAP: dict[int, Callable[[], Cell]] = {33: _nothingCell_factory}


def get_grid(path: str) -> list[list[Cell]]:
    parsed: SaveData = parse_save(path)
    cells: list[Cell] = []
    for tile in parsed.map.terrain:
        cells.append(IDMAP.get(tile[2], _nothingCell_factory)())

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
    return grid
