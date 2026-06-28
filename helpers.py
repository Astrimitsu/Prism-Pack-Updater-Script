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
        print([arg.rstrip("\\/") for arg in clean_args])
        return [arg.rstrip("\\/") for arg in clean_args]
    else:
        print(raw_args.rstrip(r"\/"))
        return raw_args.rstrip(r"\/")
        
def glob_tester(raw_path: str) -> int:
    path = Path(os.path.expandvars(raw_path))
    parent, name = Path(path.parent), path.name
    #protects against a crash if someone does something silly like look for a file in a folder
    if not parent.is_dir():
        return False
    return len(list(parent.glob(name)))
