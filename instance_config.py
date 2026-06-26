from helpers import min_max_inputs
from classes import Settings, InvalidInput
from copy import deepcopy
from pathlib import Path
import readline


def instance_config(args: list[str], settings: Settings) -> Settings:
    global instance
    new_settings: Settings = deepcopy(settings)
    syntax: str = """\
Usage:
instance                        Display all active instances
instance set <alias>            Set current instance
instance add <path> [alias]     Adds a new instance, alias defaults to folder name if not specified. Path must be surrouned by quotes.
instance remove <alias>         Removes an existing instance"""
    print(args)
    if len(args) == 1:
        print("Instances:")
        for inst in settings.config:
            print(inst)
        return new_settings

    try:
        if args[1] == "set":
            min_max_inputs(args, 2, 2)
            if args[2] not in settings.config:
                raise Exception(f"Instance {args[2]} does not exist")
            new_settings.instance = args[2]
            return new_settings

        if args[1] == "add":
            min_max_inputs(args, 2, 3)
            instancepath = Path(args[2])
            if not instancepath.exists():
                raise FileNotFoundError(f"Directory at {args[2]} does not exist")
            if not Path(instancepath / "mmc-pack.json").exists():
                raise FileNotFoundError(
                    f"Directory at {args[2]} is not a valid Prism instance"
                )

            if args[2] in settings.config:
                raise Exception(f"Specified instance at {args[2]} already exists")
            if len(args) - 1 == 3:
                new_settings.config[args[3]] = {"path": instancepath}
            if len(args) - 1 == 2:
                new_settings.config[instancepath.name] = {"path": str(instancepath)}
            return new_settings

        if args[1] == "remove":
            min_max_inputs(args, 2, 2)
            if args[2] not in settings.config:
                raise Exception(f"Specified instance {args[2]} does not exist")
            print(
                f"You are about to delete the instance: {args[2]}. Enter 'y' to continue."
            )
            if input("> ") == "y":
                del new_settings.config[args[2]]
            return new_settings
        raise InvalidInput

    except (IndexError, InvalidInput):
        print(syntax)
    except Exception as e:
        print(e)
        print(syntax)
    return new_settings