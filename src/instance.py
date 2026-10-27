from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Instance:
    path: Path
    additions: list[Path]
    removals: list[Path]

    @staticmethod
    def from_json(json_instance: dict[str, Any]):
        path: Path = Path(json_instance["path"])
        additions = [Path(addition) for addition in json_instance["additions"]]
        removals = [Path(removal) for removal in json_instance["removals"]]
        return Instance(path, additions, removals)