from helpers import shell_input
from classes import Settings, InvalidInput
from copy import deepcopy
from pathlib import Path
import os.path


def instance_config(args: list[str], settings: Settings) -> Settings:
    syntax: str = """\
Usage:
instance                        Display all active instances
instance set <alias>            Set current instance
instance add <path> [alias]     Adds a new instance, alias defaults to folder name if not specified. Path must be surrounded by quotes.
instance remove <alias>         Removes an existing instance"""

    try:
        match args:

            # display instance list
            case ["instance"]:
                print("Instances:")
                for inst in settings.config:
                    print(inst)
                return settings

            case ["instance", "help"]:
                print(syntax)
                return settings

            # set instance
            case ["instance", "set", alias]:
                if alias not in settings.config:
                    raise ValueError(f"Instance at {alias} does not exist")
                print(f"The instance {alias} is now active")
                new_settings = deepcopy(settings)
                new_settings.instance = alias
                return new_settings

            # add instance, optionally taking an alias
            case ["instance", "add", pathstr, *extra] if len(extra) <= 1:
                instancepath = Path(os.path.expandvars(pathstr))
                cleaned_extra = extra[0].strip() if extra else ""
                alias = cleaned_extra if cleaned_extra else instancepath.name

                if not instancepath.exists():
                    raise FileNotFoundError(f"Directory at {pathstr} does not exist")
                if not (instancepath / "mmc-pack.json").exists():
                    raise FileNotFoundError(
                        f"Directory at {pathstr} is not a valid Prism instance"
                    )
                if alias in settings.config:
                    raise ValueError(f"Specified instance at {alias} already exists")

                new_settings = deepcopy(settings)
                new_settings.config[alias] = {"path": str(instancepath)}
                print(f"Added instance {alias} at {pathstr} successfully!")
                return new_settings

            case ["instance", "remove", alias]:
                if alias not in settings.config:
                    raise ValueError(f"Specified instance {alias} does not exist")
                print(
                    f"You are about to delete the instance: {alias}. Enter 'y' to continue."
                )
                if shell_input(settings, string=True).strip().lower() == "y":
                    new_settings = deepcopy(settings)
                    del new_settings.config[alias]
                    if settings.instance == alias:
                        new_settings.instance = ""
                    print(f"Instance {alias} has been deleted!")
                    return new_settings
                else:
                    print("Operation cancelled")
                    return settings

            case _:
                raise InvalidInput(
                    f"{' '.join(args)} is not a recognized command or subcommand. For help, type 'instance help'"
                )

    except InvalidInput:
        print(syntax)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
    return settings
