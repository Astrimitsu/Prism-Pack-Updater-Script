from classes import Settings
import shlex
from typing import overload, Literal

@overload
def shell_input(settings: Settings, *, string: Literal[False]) -> list[str]: ...
@overload
def shell_input(settings: Settings, *, string: Literal[True]) -> str: ...
@overload
def shell_input(settings: Settings) -> list[str]: ...


def shell_input(settings: Settings, *, string=False) -> list[str] | str:
    try:
        args = shlex.split(
            input(f"{settings.instance}> " if settings.instance else "> ").replace(
                "\\", "\\\\"
            )
        )
    except KeyboardInterrupt:
        exit()
    if not string:
        clean_args = [arg.rstrip(r"\/") for arg in args]
    else:
        clean_args = " ".join(args).rstrip(r"\/")
    return clean_args
