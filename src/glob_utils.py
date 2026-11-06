import os
from pathlib import Path

import errors


def glob_counter(path: Path) -> int:
    parent, name = Path(path.parent), path.name
    if not parent.is_dir():
        raise NotADirectoryError(errors.ERR_NOT_DIRECTORY.format(path))
    return len(list(parent.glob(name)))


def expand_glob(path: Path) -> list[Path]:
    test_path = Path(path)
    parent, name = Path(test_path.parent), test_path.name
    if parent.exists():
        return list(parent.glob(name))
    else:
        return []


def check_glob_collisions(a: Path, b: Path) -> bool:
    globbed_a: set[Path] = set(expand_glob(Path(os.path.expandvars(a))))
    globbed_b: set[Path] = set(expand_glob(Path(os.path.expandvars(b))))
    return not globbed_a.isdisjoint(globbed_b)


def assert_glob_single_match(path: Path) -> None:
    glob_matches = glob_counter(path)
    if glob_matches == 0:
        raise FileNotFoundError(errors.ERR_FILE_NOT_EXIST.format(path))
    if glob_matches > 1:
        raise ValueError(errors.ERR_GLOB_TOO_MANY_MATCHES.format(path))
