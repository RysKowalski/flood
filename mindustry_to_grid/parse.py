import io
import struct
import zlib
import pickle
from typing import BinaryIO, Any
from dataclasses import dataclass
from typing import Optional


# -------------------------
# Binary helpers
# -------------------------


def read(fmt: str, f: BinaryIO) -> tuple[int, ...]:
    size = struct.calcsize(fmt)
    data = f.read(size)
    return struct.unpack(fmt, data)


def read_i32(f: BinaryIO) -> int:
    return read(">i", f)[0]


def read_i16(f: BinaryIO) -> int:
    return read(">h", f)[0]


def read_u16(f: BinaryIO) -> int:
    return read(">H", f)[0]


def read_u8(f: BinaryIO) -> int:
    return read(">B", f)[0]


def read_bool(f: BinaryIO) -> bool:
    return read_u8(f) != 0


def read_utf(f: BinaryIO) -> str:
    length = read_u16(f)
    return f.read(length).decode("utf-8")


def read_chunk(f: BinaryIO) -> io.BytesIO:
    length = read_i32(f)
    data = f.read(length)
    return io.BytesIO(data)


# -------------------------
# Dataclasses
# -------------------------


@dataclass
class Core:
    x: int
    y: int
    type: str


@dataclass
class Block:
    index: int
    block_id: int
    name: str
    entity: bool
    data: Optional[bytes] = None
    building_revision: Optional[int] = None
    run: Optional[int] = None


@dataclass
class MapData:
    width: int
    height: int
    terrain: list[tuple[int, int, int]]
    blocks: list[Block]
    cores: list[Core]


@dataclass
class SaveData:
    version: int
    block_map: dict[int, str]
    map: MapData


# -------------------------
# Parsing
# -------------------------


def parse_content(f: BinaryIO) -> dict[int, str]:
    block_map: dict[int, str] = {}

    mapped = read_u8(f)

    for _ in range(mapped):
        _content_type = read_u8(f)
        count = read_u16(f)

        names = [read_utf(f) for _ in range(count)]

        for i, name in enumerate(names):
            block_map[i] = name

    return block_map


def parse_map(f: BinaryIO, block_map: dict[int, str]) -> MapData:
    width = read_u16(f)
    height = read_u16(f)
    total = width * height

    terrain: list[tuple[int, int, int]] = []
    blocks: list[Block] = []
    cores: list[Core] = []

    # --- terrain ---
    i = 0
    while i < total:
        floor_id = read_i16(f)
        overlay_id = read_i16(f)
        run = read_u8(f)

        terrain.append((floor_id, overlay_id, run))
        i += run + 1

    # --- blocks ---
    i = 0
    while i < total:
        block_id = read_i16(f)
        packed = read_u8(f)

        had_entity = (packed & 1) != 0
        had_data = (packed & 4) != 0

        name = block_map.get(block_id, f"<unknown:{block_id}>")

        entry = Block(
            index=i,
            block_id=block_id,
            name=name,
            entity=had_entity,
        )

        if had_data:
            entry.data = f.read(1 + 1 + 1 + 4)

        is_center = True
        if had_entity:
            is_center = read_bool(f)

        if name.startswith("core-") and is_center:
            cores.append(Core(x=i % width, y=i // width, type=name))

        if had_entity:
            if is_center:
                chunk = read_chunk(f)
                entry.building_revision = read_u8(chunk)

        elif not had_data:
            run = read_u8(f)
            entry.run = run
            i += run

        blocks.append(entry)
        i += 1

    return MapData(
        width=width,
        height=height,
        terrain=terrain,
        blocks=blocks,
        cores=cores,
    )


def parse_save(path: str) -> SaveData:
    with open(path, "rb") as fp:
        raw = fp.read()

    data = zlib.decompress(raw)
    f = io.BytesIO(data)
    header: bytes = b"MSAV"
    actual = f.read(len(header))
    if actual != header:
        raise ValueError("invalid header")

    version = read_i32(f)

    _ = read_chunk(f)  # meta ignored

    content_chunk = read_chunk(f)
    block_map = parse_content(content_chunk)

    if version >= 11:
        _ = read_chunk(f)

    map_chunk = read_chunk(f)
    map_data = parse_map(map_chunk, block_map)

    return SaveData(
        version=version,
        block_map=block_map,
        map=map_data,
    )


# -------------------------
# Serialization
# -------------------------


def save_pickle(data: SaveData, output_path: str) -> None:
    """Serialize parsed data into a pickle file."""
    with open(output_path, "wb") as fp:
        pickle.dump(data, fp)


# -------------------------
# Entry point
# -------------------------

if __name__ == "__main__":
    parsed = parse_save("./testSaveSmall.msav")
    save_pickle(parsed, "./parsed_map.pickle")
