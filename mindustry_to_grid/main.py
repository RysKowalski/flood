from flood_types import Cell, CellType
from .parse import parse_save, SaveData


def get_grid(path: str) -> list[list[Cell]]:
    parsed: SaveData = parse_save(path)
    grid: list[list[Cell]] = _create_grid(parsed.map.width, parsed.map.height)

    return grid


def _create_grid(width: int, height: int) -> list[list[Cell]]:
    return [[Cell(CellType.NOTHING, 0.0) for _ in range(height)] for _ in range(width)]
