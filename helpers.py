from classes import InvalidInput, Settings
import shlex


def min_max_inputs(args: list, min: int, max: int) -> None:
    if len(args) - 1 < min or len(args) - 1 > max:
        print("maxinput triggered")
        raise InvalidInput


def shell_input(settings: Settings) -> list[str]:
    try:
        args = shlex.split(
            input(f"{settings.instance}> " if settings.instance else "> ").replace(
                "\\", "\\\\"
            )
        )
    except KeyboardInterrupt:
        exit()
    clean_args = [arg.strip(r"\/") for arg in args]
    return clean_args