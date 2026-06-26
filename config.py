from classes import Settings
from helpers import shell_input
from instance_config import instance_config
from mod_config import mod_config


def config(settings: Settings) -> None:
    new_settings = settings

    while True:
        args = shell_input(settings)
        if args[0] == "instance":
            new_settings = instance_config(args, settings)
        if args[0] == "mod":
            new_settings = mod_config(args, settings)

        if new_settings.config != settings.config:
            new_settings.write_to_json()
        if new_settings != settings:
            settings = new_settings
