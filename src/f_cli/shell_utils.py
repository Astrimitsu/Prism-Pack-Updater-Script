import platform
import shlex
from typing import Literal, overload

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
    return shlex.split(raw_args)


def clean_input(args: list[str]) -> list[str]:
    return [arg.replace("\\", "/") for arg in args]

def strip_script_name(args: list[str]) -> list[str]:
    return args if not args[0].endswith(".py") else args[:1]
