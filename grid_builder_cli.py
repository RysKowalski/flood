from __future__ import annotations

import curses

from flood_types import Cell, CellType


class GridTUI:
    """
    Curses-based grid editor.
    Grid indexing: grid[x][y].
    """

    SYMBOLS: dict[CellType, str] = {
        CellType.NOTHING: ".",
        CellType.WALL: "#",
        CellType.GENERATOR: "G",
        CellType.VOID: "V",
    }

    KEYMAP: dict[int, CellType] = {ord(str(t.value)): t for t in CellType}

    def __init__(self, width: int, height: int) -> None:
        self.width: int = width
        self.height: int = height
        self.grid: list[list[Cell]] = self._create_grid()

        self.cx: int = 0
        self.cy: int = 0
        self.show_help: bool = False

    def _create_grid(self) -> list[list[Cell]]:
        return [
            [Cell(CellType.NOTHING, 0.0) for _ in range(self.height)]
            for _ in range(self.width)
        ]

    def _set(self, x: int, y: int, t: CellType) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[x][y] = Cell(t, 0.0)

    def _symbol(self, t: CellType) -> str:
        return self.SYMBOLS.get(t, str(t.value))

    def _render(self, stdscr: curses.window) -> None:
        stdscr.clear()

        max_y, max_x = stdscr.getmaxyx()

        for y in range(self.height):
            if y >= max_y - 1:
                break

            row: str = ""
            for x in range(self.width):
                ch: str = self._symbol(self.grid[x][y].type)

                if x == self.cx and y == self.cy:
                    row += f"[{ch}]"
                else:
                    row += f" {ch} "

            stdscr.addnstr(y, 0, row, max_x - 1)

        offset: int = self.height + 1

        if offset < max_y:
            bindings: str = " | ".join(
                f"{t.value}: {self._symbol(t)}" for t in CellType
            )

            stdscr.addnstr(
                offset,
                0,
                f"Arrows: move | {bindings} | q: quit | h: help",
                max_x - 1,
            )

        if self.show_help:
            help_lines: list[str] = [
                "Help:",
                "Move cursor and paint cells directly.",
                "Grid is indexed as grid[x][y].",
            ]

            for i, line in enumerate(help_lines):
                y_pos: int = offset + 2 + i
                if y_pos >= max_y:
                    break
                stdscr.addnstr(y_pos, 0, line, max_x - 1)

        stdscr.refresh()

    def _handle_key(self, key: int) -> bool:
        if key == ord("q"):
            return False

        if key == ord("h"):
            self.show_help = not self.show_help
            return True

        if key == curses.KEY_LEFT:
            self.cx = max(0, self.cx - 1)
        elif key == curses.KEY_RIGHT:
            self.cx = min(self.width - 1, self.cx + 1)
        elif key == curses.KEY_UP:
            self.cy = max(0, self.cy - 1)
        elif key == curses.KEY_DOWN:
            self.cy = min(self.height - 1, self.cy + 1)

        elif key in self.KEYMAP:
            self._set(self.cx, self.cy, self.KEYMAP[key])

        return True

    def run(self, stdscr: curses.window) -> list[list[Cell]]:
        curses.curs_set(0)
        stdscr.keypad(True)

        running: bool = True
        while running:
            self._render(stdscr)
            key: int = stdscr.getch()
            running = self._handle_key(key)

        return self.grid


def tui(width: int, height: int) -> list[list[Cell]]:
    """
    Launch curses TUI and return final grid.
    """
    builder = GridTUI(width, height)
    return curses.wrapper(builder.run)
