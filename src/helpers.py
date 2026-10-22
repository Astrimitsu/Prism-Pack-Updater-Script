import os
import platform
import shlex
from pathlib import Path
from typing import Any, Literal, overload

if platform.system() == "Linux":
    import readline  # noqa: F401


@overload
def shell_input(prompt: str, *, string: Literal[False]) -> list[str]: ...
@overload
def shell_input(prompt: str, *, string: Literal[True]) -> str: ...
@overload
def shell_input(prompt: str) -> list[str]: ...


def shell_input(prompt: str = "", *, string=False) -> list[str] | str:
    raw_args = input(f"{prompt}> ")
    if string:
        return raw_args
    return shlex.split(raw_args.replace("\\", "/"))


def path_preprocessor(raw_args: list[Any], args_to_convert: list[int]):
    new_args = raw_args.copy()
    for i in args_to_convert:
        new_args[i] = Path(os.path.expandvars(raw_args[i]))
    return new_args


# TODO: Implement this earlier in the chain: path =
def glob_counter(path: Path) -> int:
    parent, name = Path(path.parent), path.name
    # return 0 if attempting to glob inside a file
    if not parent.is_dir():
        return 0
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
        raise FileNotFoundError(f"File at {path} does not exist")
    if glob_matches > 1:
        raise ValueError(f"Input {path} resolves to more than one file")


def json_serializer_helper(obj: object) -> object:
    match obj:
        case Path():
            return str(obj)
        case _:
            raise TypeError(
                f"Object of type {type(obj).__name__} is not JSON serializable"
            )
