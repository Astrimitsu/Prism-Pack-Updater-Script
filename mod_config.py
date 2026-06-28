from classes import Settings, InvalidInput
from helpers import glob_tester
from copy import deepcopy


def mod_config(args: list[str], settings: Settings) -> Settings:
    syntax = """
Usage:
mod                                     Display all active additions and removals
mod addition <add|remove> <mod name>    Add or remove an addition to the modlist
mod removal <add|remove> <mod name>     Add or remove a removal from the modlist"""

    if not settings.instance:
        print("Instance not set: Create and set instance first")
        return settings
    additions = settings.config[settings.instance].get("additions")
    removals = settings.config[settings.instance].get("removals")

    try:
        match args:

            case ["mod", "help"]:
                print(syntax)
                return settings

            case ["mod"]:
                print(f"Additions: {"\n".join(additions) if additions else "None"}")
                print(f"Removals: {"\n".join(removals) if removals else "None"}")
                return settings
            
            case ["mod", action_type, action, new_mod]:
                directory = f"{settings.mod_dir}/{new_mod.lstrip("\\/")}"
                if action_type.lower() not in ("addition", "removal"):
                    raise InvalidInput
                if action not in ("add", "remove"):
                    raise InvalidInput
                glob_matches = glob_tester(directory)
                if glob_matches == 0:
                    raise FileNotFoundError(f"File at {directory} does not exist")
                if glob_matches > 1:
                    raise ValueError(f"Input at {directory} can resolve to more than one file")
                
                print("Success!")

                


            case _:
                raise InvalidInput

    except (ValueError, FileNotFoundError) as e:
        print(e)
    except InvalidInput:
        print(f"No command '{" ".join(args)}' exists. For help, use 'mod help'")
    return settings
