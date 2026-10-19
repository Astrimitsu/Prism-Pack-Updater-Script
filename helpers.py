import os.path
import platform
import shlex
from pathlib import Path
from typing import Literal, overload

from Settings import Settings

if platform.system() == "Linux":
    import readline  # noqa: F401


@overload
def shell_input(settings: Settings, *, string: Literal[False]) -> list[str]: ...
@overload
def shell_input(settings: Settings, *, string: Literal[True]) -> str: ...
@overload
def shell_input(settings: Settings) -> list[str]: ...


def shell_input(settings: Settings, *, string=False) -> list[str] | str:
    raw_args = input(f"{settings.instance}> " if settings.instance else "> ")
    if string:
        return raw_args
    return shlex.split(raw_args.replace("\\", "/"))


# TODO: Implement this earlier in the chain: path = Path(os.path.expandvars(raw_path))
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


# test_path should always be ensured to have only one possible result with the glob tester above!
def glob_duplicate_test(
    test_path: str, existing_list: list, settings: Settings
) -> bool:
    path = Path(os.path.expandvars(test_path))
    assert_glob_single_match(path)
    globbed_test_item = expand_glob(path)[0]

    globbed_paths = {
        glob
        for item in existing_list
        for glob in expand_glob(settings.path_to_instance_folder(item))
    }

    return globbed_test_item in globbed_paths


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
