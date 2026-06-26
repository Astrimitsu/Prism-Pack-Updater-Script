from copy import deepcopy
from classes import Settings
from instance_config import instance_config
import readline
import shlex


def main() -> None:

    settings = Settings()
    config(settings)


def config(settings: Settings) -> None:
    new_settings = deepcopy(settings)

    while True:
        print(settings.instance)
        try:
            args: list = shlex.split(input(
                f"{settings.instance}>" if settings.instance else "> "
            ).strip('\\/'))
        except KeyboardInterrupt:
            print("\n")
            exit()
        if args[0] == "instance":
            new_settings = instance_config(args, settings)
        if args[0] == "mod":
            new_settings = mod_config(args, settings)

        if new_settings.config != settings.config:
            new_settings.write_to_json()
        if new_settings != settings:
            settings = new_settings


def mod_config(args: list[str], settings: Settings) -> Settings:
    new_settings = deepcopy(settings)
    syntax = """\
Usage:
mod                                 Display all active additions and removals
mod addition <add|remove> <path>    Add or remove an addition to the modlist
mod removal <add|remove> <path>     Add or remove a removal from the modlist"""
    try:
        if not settings.instance:
            print("Instance not set: Create and set instance first")

    except Exception as e:
        print(e)
        print(syntax)

    return new_settings


main()
