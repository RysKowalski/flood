from flood_types import Cell, CellType


class GridBuilder:
    """
    Interactive grid builder with CLI controls and live visualization.
    Grid is indexed as grid[x][y].
    """

    SYMBOLS: dict[CellType, str] = {
        CellType.NOTHING: ".",
        CellType.WALL: "#",
        CellType.GENERATOR: "G",
    }

    def __init__(self, width: int, height: int) -> None:
        self.width: int = width
        self.height: int = height
        self.grid: list[list[Cell]] = self._create_grid()

    def _create_grid(self) -> list[list[Cell]]:
        return [
            [Cell(CellType.NOTHING, 0.0) for _ in range(self.height)]
            for _ in range(self.width)
        ]

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def parse_cell_type(self, token: str) -> CellType:
        key: str = token.strip().upper()
        try:
            return CellType[key]
        except KeyError:
            raise ValueError(f"Unknown CellType: {token}")

    def set_cell(self, x: int, y: int, cell_type: CellType) -> None:
        if self._in_bounds(x, y):
            self.grid[x][y] = Cell(cell_type, 0.0)

    def clear_cell(self, x: int, y: int) -> None:
        self.set_cell(x, y, CellType.NOTHING)

    def set_line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        cell_type: CellType,
    ) -> None:
        if x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.set_cell(x1, y, cell_type)

        elif y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.set_cell(x, y1, cell_type)

        else:
            print("Line must be strictly horizontal or vertical.")

    def render(self) -> None:
        print("\nCurrent Grid:")
        for y in range(self.height):
            print(
                " ".join(
                    self.SYMBOLS.get(self.grid[x][y].type, "?")
                    for x in range(self.width)
                )
            )
        print()

    def help(self) -> None:
        print(
            "Commands:\n"
            "  set x y type         -> set cell type (e.g. wall, generator)\n"
            "  clear x y            -> set cell to nothing\n"
            "  line x1 y1 x2 y2 t   -> draw line with type t\n"
            "  types                -> show available cell types\n"
            "  show                 -> redraw grid\n"
            "  help                 -> show commands\n"
            "  quit                 -> exit\n"
        )

    def show_types(self) -> None:
        print("Available types:")
        for t in CellType:
            print(t.name.lower())

    def cli(self) -> list[list[Cell]]:
        self.render()
        self.help()

        while True:
            command: list[str] = input("> ").strip().split()
            if not command:
                continue

            action: str = command[0].lower()

            if action == "quit":
                return self.grid

            if action == "help":
                self.help()
                continue

            if action == "show":
                self.render()
                continue

            if action == "types":
                self.show_types()
                continue

            try:
                if action == "clear" and len(command) == 3:
                    self.clear_cell(int(command[1]), int(command[2]))
                    self.render()
                    continue

                if action == "set" and len(command) == 4:
                    x: int = int(command[1])
                    y: int = int(command[2])
                    cell_type: CellType = self.parse_cell_type(command[3])
                    self.set_cell(x, y, cell_type)
                    self.render()
                    continue

                if action == "line" and len(command) == 6:
                    x1: int = int(command[1])
                    y1: int = int(command[2])
                    x2: int = int(command[3])
                    y2: int = int(command[4])
                    cell_type: CellType = self.parse_cell_type(command[5])
                    self.set_line(x1, y1, x2, y2, cell_type)
                    self.render()
                    continue

            except ValueError as e:
                print(f"Invalid input: {e}")
                continue

            print("Unknown command. Type 'help'.")


def cli(width: int, height: int) -> list[list[Cell]]:
    builder = GridBuilder(width, height)
    return builder.cli()
