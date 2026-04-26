from __future__ import annotations

import pickle
import json
from dataclasses import asdict, is_dataclass
from typing import Any
from parse import SaveData, MapData, Block, Core


def convert_value(value: Any) -> Any:
    """Recursively convert non-JSON-serializable values into JSON-compatible ones."""

    if is_dataclass(value):
        return convert_value(asdict(value))

    if isinstance(value, dict):
        return {str(k): convert_value(v) for k, v in value.items()}

    if isinstance(value, list):
        return [convert_value(v) for v in value]

    if isinstance(value, tuple):
        return [convert_value(v) for v in value]

    if isinstance(value, (bytes, bytearray)):
        return list(value)

    return value


def load_save_data(pickle_path: str) -> Any:
    """Load SaveData object from a pickle file."""
    with open(pickle_path, "rb") as f:
        return pickle.load(f)


def save_as_json(obj: Any, json_path: str) -> None:
    """Serialize object to pretty JSON file."""
    data = convert_value(obj)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main() -> None:
    pickle_path: str = "parsed_map.pickle"
    json_path: str = "data.json"

    save_data = load_save_data(pickle_path)
    save_as_json(save_data, json_path)


if __name__ == "__main__":
    main()
