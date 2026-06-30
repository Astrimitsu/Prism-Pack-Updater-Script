from classes import Settings, InvalidInput
from helpers import glob_tester, glob_duplicate_test
from copy import deepcopy


def file_config(args: list[str], settings: Settings) -> Settings:
    syntax = """
Usage:
manage                                     Display all active additions and removals
manage additions <add|remove> <mod name>    Add or remove an addition to the modlist
manage removals <add|remove> <mod name>     Add or remove a removal from the modlist
manage help                               Display this help text"""

    if not settings.instance:
        print("Instance not set: Create and set instance first")
        return settings
    additions = settings.config[settings.instance].get("additions")
    removals = settings.config[settings.instance].get("removals")

    try:
        match args:

            case ["manage"]:
                print(f"Additions: {"\n".join(additions) if additions else "None"}")
                print(f"Removals: {"\n".join(removals) if removals else "None"}")
                return settings

            case ["manage", "help"]:
                print(syntax)
                return settings

            case ["manage", action_type, action, new_path]:
                directory = f"minecraft/{new_path.lstrip("\\/")}"
                full_directory = f"{settings.config[settings.instance]["path"]}/minecraft/{new_path.strip("\\/")}"
                if action_type not in ("additions", "removals"):
                    raise InvalidInput
                if action not in ("add", "remove"):
                    raise InvalidInput
                glob_matches = glob_tester(full_directory)
                if glob_matches == 0:
                    raise FileNotFoundError(f"File at {directory} does not exist")
                if glob_matches > 1:
                    raise ValueError(
                        f"Input {directory} resolves to more than one file"
                    )

                new_settings = deepcopy(settings)
                if action_type not in new_settings.config[settings.instance]:
                    new_settings.config[settings.instance][action_type] = []
                target_list = new_settings.config[new_settings.instance][action_type]
                if action == "add":
                    if not glob_duplicate_test(full_directory, target_list, settings):
                        target_list.append(new_path)
                        print(f"File {action_type[:-1]} at {new_path} has been added!")
                    else:
                        raise ValueError(
                            f"Input {new_path} resolves to an already existing {action_type[:-1]}"
                        )
                elif action == "remove":
                    if new_path in target_list:
                        target_list.remove(new_path)
                        print(
                            f"File {action_type[:-1]} at {new_path} has been removed! "
                        )
                    else:
                        print(f"File {action_type[:-1]} at {new_path} does not exist")
                return new_settings

            case _:
                raise InvalidInput

    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
    except InvalidInput:
        print(f"No command '{" ".join(args)}' exists. For help, use 'manage help'")
    return settings
