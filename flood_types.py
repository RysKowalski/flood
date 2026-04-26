from dataclasses import dataclass
from enum import Enum


class CellType(Enum):
    NOTHING = 1
    WALL = 2
    GENERATOR = 3
    VOID = 4


@dataclass
class Cell:
    type: CellType
    value: float
