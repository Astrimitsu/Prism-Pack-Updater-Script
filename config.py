from classes import Settings
from file_config import file_config
from helpers import shell_input


def config() -> Settings:
    settings = Settings()
    new_settings = settings
    syntax = """\
Usage: 
help                        Display this help text
instance                    Modify instances, or set current instance
manage                      Add or remove files or folders from the pack
run                         Start migration process

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
            case ["run"]:
                if settings.instance:
                    break
                else:
                    print("Instance not set: Create and set instance first")
            case _:
                print("Unknown command. Type 'help' for help.")

        settings.write_to_json()

    if settings != new_settings:
        settings = new_settings
    return settings    
