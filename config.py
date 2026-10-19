from helpers import shell_input
from settings import Settings


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

        settings.write_to_json()

    if settings != new_settings:
        settings = new_settings
    return settings
