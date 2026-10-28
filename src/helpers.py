import os
import platform
import shlex
from pathlib import Path
from typing import Any, Literal, overload

import str_templates

if platform.system() == "Linux":
    import readline  # noqa: F401


@overload
def shell_input(prompt: str | None, *, string: Literal[False]) -> list[str]: ...
@overload
def shell_input(prompt: str | None, *, string: Literal[True]) -> str: ...
@overload
def shell_input(prompt: str | None) -> list[str]: ...


def shell_input(prompt: str | None = None, *, string=False) -> list[str] | str:
    raw_args = input(f"{prompt if prompt else ""}> ").strip()
    if string:
        return raw_args
    return shlex.split(raw_args.replace("\\", "/"))


def path_preprocessor(raw_args: list[Any], args_to_convert: list[int]):
    new_args = raw_args.copy()
    for i in args_to_convert:
        new_args[i] = Path(os.path.expandvars(raw_args[i]))
    return new_args


def glob_counter(path: Path) -> int:
    parent, name = Path(path.parent), path.name
    if not parent.is_dir():
        raise NotADirectoryError(str_templates.ERR_NOT_DIRECTORY.format(path))
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
        raise FileNotFoundError(str_templates.ERR_FILE_NOT_EXIST.format(path))
    if glob_matches > 1:
        raise ValueError(str_templates.ERR_GLOB_TOO_MANY_MATCHES.format(path))
