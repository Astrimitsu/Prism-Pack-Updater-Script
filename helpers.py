from classes import Settings
import shlex
from typing import overload, Literal
import sys
from pathlib import Path
import os.path
import platform

if platform.system() == "Linux":
    import readline  # noqa: F401


@overload
def shell_input(settings: Settings, *, string: Literal[False]) -> list[str]: ...
@overload
def shell_input(settings: Settings, *, string: Literal[True]) -> str: ...
@overload
def shell_input(settings: Settings) -> list[str]: ...


def shell_input(settings: Settings, *, string=False) -> list[str] | str:
    try:
        raw_args = input(f"{settings.instance}> " if settings.instance else "> ")
    except KeyboardInterrupt:
        print()
        sys.exit(0)
    if not string:
        try:
            clean_args = shlex.split(raw_args.replace("\\", "\\\\"))
        except ValueError as e:
            print(f"Syntax Error: {e}")
            return []
        return [arg.rstrip("\\/") for arg in clean_args]
    else:
        return raw_args.rstrip(r"\/")


def glob_tester(raw_path: str) -> int:
    path = Path(os.path.expandvars(raw_path))
    parent, name = Path(path.parent), path.name
    # return 0 (does not exist) if attempting to glob inside a file
    if not parent.is_dir():
        return 0
    return len(list(parent.glob(name)))


# test_path should always be ensured to have only one possible result with the glob tester above!
def glob_duplicate_test(test_path: str, existing_list: list, settings: Settings) -> bool:
    path = Path(os.path.expandvars(test_path))

    def expand_glob(item):
        test_path = Path(item)
        parent, name = Path(test_path.parent), test_path.name
        if parent.exists():
            return parent.glob(name)
        else:
            return []

    globbed_paths = set()
    for item in existing_list:
        for glob in expand_glob(expand_path(item, settings)):
            if glob:
                globbed_paths.add(glob)
    globbed_test_item = []
    for glob in expand_glob(path):
        globbed_test_item.append(glob)
    return globbed_test_item[0] in globbed_paths


def expand_path(path: str, settings: Settings) -> str:
    return f"{settings.config[settings.instance]["path"]}/minecraft/{path.strip("\\/")}"
