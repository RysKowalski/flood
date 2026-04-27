from PIL import Image
import io
import base64


from typing import Optional

from flood_types import Cell, CellType


class Flood:
    def __init__(
        self,
        size: tuple[int, int],
        floodMap: Optional[list[list[Cell]]] = None,
    ) -> None:
        if floodMap is None:
            self.size: tuple[int, int] = size  # (width, height)
            self.cells: list[list[Cell]] = [
                [Cell(CellType.NOTHING, 0) for _ in range(size[1])]
                for _ in range(size[0])
            ]
        else:
            self.size = len(floodMap), len(floodMap[0])
            self.cells = floodMap

        self.neighbors: list[list[int]]
        self._calculate_neighbors()

    def _calculate_neighbors(self) -> None:
        """Compute the number of orthogonal neighbors for each cell."""
        width: int
        height: int
        width, height = self.size

        self.neighbors = [[0 for _ in range(height)] for _ in range(width)]

        for x in range(width):
            for y in range(height):
                count: int = 0

                if x > 0:
                    count += 1
                if x < width - 1:
                    count += 1
                if y > 0:
                    count += 1
                if y < height - 1:
                    count += 1

                self.neighbors[x][y] = count

    def draw(self) -> str:
        cells = self.cells
        if not cells:
            return ""

        width: int = max(len(row) for row in cells)
        horizontal: str = "+" + "-----+" * width

        lines: list[str] = []
        lines.append(horizontal)

        for row in cells:
            row_len = len(row)

            parts: list[str] = ["|"]

            # process existing cells
            for i in range(row_len):
                cell = row[i]

                val = cell.value
                text = f"{val:5.1f}"

                parts.append(text)
                parts.append("|")

            # pad remaining cells without creating new Cell objects
            for _ in range(width - row_len):
                parts.append(f"{0.0:5.1f}")
                parts.append("|")

            lines.append("".join(parts))
            lines.append(horizontal)

        return "\n".join(lines)

    def draw_color(self) -> str:
        """Return a string representation of the float grid with borders (1 decimal place) and colored cells based on CellType."""
        cells = self.cells
        if not cells:
            return ""

        RESET: str = "\033[0m"

        rgb = self._rgb
        WALL_COLOR: str = rgb(0, 255, 0)
        GENERATOR_COLOR: str = rgb(160, 160, 0)
        BLUE_COLOR: str = rgb(0, 0, 255)

        width: int = max(len(row) for row in cells)
        horizontal: str = "+" + "-----+" * width

        lines: list[str] = []
        lines.append(horizontal)

        for row in cells:
            row_len = len(row)

            parts: list[str] = ["|"]

            # process existing cells
            for i in range(row_len):
                cell = row[i]

                val = cell.value
                text = f"{val:5.1f}"

                t = cell.type
                if t is CellType.WALL:
                    parts.append(WALL_COLOR)
                    parts.append(text)
                    parts.append(RESET)
                elif t is CellType.GENERATOR:
                    parts.append(GENERATOR_COLOR)
                    parts.append(text)
                    parts.append(RESET)
                elif t is CellType.NOTHING and val > 0.05:
                    parts.append(BLUE_COLOR)
                    parts.append(text)
                    parts.append(RESET)
                else:
                    parts.append(text)

                parts.append("|")

            # pad remaining cells without creating new Cell objects
            for _ in range(width - row_len):
                parts.append(f"{0.0:5.1f}")
                parts.append("|")

            lines.append("".join(parts))
            lines.append(horizontal)

        return "\n".join(lines)

    @staticmethod
    def _rgb(r: int, g: int, b: int) -> str:
        """Return ANSI escape sequence for 24-bit RGB foreground color."""
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return f"\033[38;2;{r};{g};{b}m"

    def draw_color_boxes(self) -> str:
        cells = self.cells
        if not cells:
            return ""

        RESET: str = "\033[0m"

        rgb = self._rgb
        WALL_COLOR: str = rgb(0, 255, 0)
        GENERATOR_COLOR: str = rgb(160, 160, 0)
        BLUE_COLOR: str = rgb(0, 0, 255)

        width: int = max(len(row) for row in cells)

        lines: list[str] = []

        for row in cells:
            row_len = len(row)

            parts: list[str] = []
            box = "█"

            # process existing cells
            for i in range(row_len):
                cell = row[i]

                t = cell.type
                if t is CellType.WALL:
                    parts.append(WALL_COLOR)
                    parts.append(box)
                    parts.append(RESET)
                elif t is CellType.GENERATOR:
                    parts.append(GENERATOR_COLOR)
                    parts.append(box)
                    parts.append(RESET)
                elif t is CellType.NOTHING and cell.value > 0.05:
                    parts.append(BLUE_COLOR)
                    parts.append(box)
                    parts.append(RESET)
                else:
                    parts.append(box)

            # pad remaining cells without creating new Cell objects
            for _ in range(width - row_len):
                parts.append(box)

            lines.append("".join(parts))

        return "\n".join(lines)

    def draw_sixel(self) -> str:
        cells = self.cells
        if not cells:
            return ""

        height: int = len(cells)
        width: int = max(len(row) for row in cells)

        def get_color(cell) -> int:
            if cell.type is CellType.WALL:
                return 1
            if cell.type is CellType.GENERATOR:
                return 2
            if cell.type is CellType.NOTHING and cell.value > 0.05:
                return 3
            return 0

        # Build indexed grid
        grid: list[list[int]] = []
        for y in range(height):
            row = cells[y]
            grid.append(
                [get_color(row[x]) if x < len(row) else 0 for x in range(width)]
            )

        out: list[str] = []
        out.append("\x1bPq")

        # palette
        out.append("#0;2;0;0;0")
        out.append("#1;2;0;255;0")
        out.append("#2;2;160;160;0")
        out.append("#3;2;0;0;255")

        for y0 in range(0, height, 6):
            band = grid[y0 : y0 + 6]

            for x in range(width):
                # group by color
                buckets: dict[int, int] = {}

                for bit in range(6):
                    if bit >= len(band):
                        continue
                    color = band[bit][x]
                    buckets[color] = buckets.get(color, 0) | (1 << bit)

                for color, bits in buckets.items():
                    out.append(f"#{color}")
                    out.append(chr(0x3F + bits))

                out.append("$")
            out.append("-")

        out.append("\x1b\\")
        return "".join(out)

    def draw_kitty(self) -> str:
        """
        Render the cell grid as a Kitty graphics protocol image string.
        Requires a Kitty-compatible terminal.
        """

        cells = self.cells
        if not cells:
            return ""

        height: int = len(cells)
        width: int = max(len(row) for row in cells)

        def get_rgb(cell) -> tuple[int, int, int]:
            if cell.type is CellType.WALL:
                return (0, 255, 0)
            if cell.type is CellType.GENERATOR:
                return (160, 160, 0)
            if cell.type is CellType.NOTHING and cell.value > 0.05:
                return (0, 0, 255)
            return (0, 0, 0)

        # Build image
        img: Image.Image = Image.new("RGB", (width, height))
        pixels = img.load()

        for y in range(height):
            row = cells[y]
            for x in range(width):
                cell = row[x] if x < len(row) else None
                pixels[x, y] = get_rgb(cell) if cell else (0, 0, 0)

        # Encode PNG in memory
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        data = buffer.getvalue()

        # Kitty graphics protocol (direct transmission, no chunking)
        b64 = base64.b64encode(data).decode("ascii")

        return "\x1b_Ga=T,f=100,t=d;" + b64 + "\x1b\\"

    def tick(self) -> None:
        self._tick_flood()
        self._tick_generators()
        self._tick_voids()

    def _tick_generators(self) -> None:
        width, height = self.size
        for x in range(width):
            for y in range(height):
                if self.cells[x][y].type == CellType.GENERATOR:
                    self.cells[x][y].value += 10

    def _tick_voids(self) -> None:
        width, height = self.size
        for x in range(width):
            for y in range(height):
                if self.cells[x][y].type == CellType.VOID:
                    self.cells[x][y].value = 0

    def _tick_flood(self) -> None:
        width, height = self.size
        k: float = 0.1

        new_values: list[list[float]] = [
            [self.cells[x][y].value for y in range(height)] for x in range(width)
        ]

        directions: list[tuple[int, int]] = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]

        for x in range(width):
            for y in range(height):
                if not self._is_floodable(x, y):
                    continue

                v: float = self.cells[x][y].value
                if v <= 0:
                    continue

                for dx, dy in directions:
                    nx: int = x + dx
                    ny: int = y + dy

                    if not self._is_floodable(nx, ny):
                        continue

                    delta: float = self.cells[nx][ny].value - v
                    flow: float = k * delta

                    new_values[x][y] += flow
                    new_values[nx][ny] -= flow

        for x in range(width):
            for y in range(height):
                self.cells[x][y].value = new_values[x][y]

    def _is_floodable(self, x: int, y: int) -> bool:
        width: int
        height: int
        width, height = self.size

        if x < 0 or x >= width:
            return False
        if y < 0 or y >= height:
            return False

        if self.cells[x][y].type is CellType.WALL:
            return False

        return True


if __name__ == "__main__":
    from mindustry_to_grid.main import get_grid

    flood: Flood = Flood((1, 1), get_grid("mindustry_to_grid/testSquare.msav"))
    try:
        while True:
            print(flood.draw_kitty())
            print()
            flood.tick()
    except KeyboardInterrupt:
        exit()
