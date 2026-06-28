from classes import Settings
from helpers import shell_input
from instance_config import instance_config
from file_config import file_config


def config(settings: Settings) -> None:
    # this should always be overwritten by a deep copy
    new_settings = settings
    syntax = """\
Usage: 
instance                    Modify instances, or set current instance.
mod                         Add or remove mods from the pack
config                      Add or remove a config file or folder from the pack
help                        Display this help text
For more help, type the command you want, then 'help'"""
    print(syntax)
    while True:
        args = shell_input(settings)
        match args:
            case ["help"]:
                print(syntax)
            case ["instance", *_]:
                new_settings = instance_config(args, settings)
            case ["manage", *_]:
                new_settings = file_config(args, settings)
            case _:
                print("Unknown command. Type 'help' for help.")

        if new_settings.config != settings.config:
            new_settings.write_to_json()
        if new_settings != settings:
            settings = new_settings
