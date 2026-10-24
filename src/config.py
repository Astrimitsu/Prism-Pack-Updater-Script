from helpers import shell_input
from settings import Settings


def config() -> Settings:
    settings = Settings.from_disk()
    syntax = """\
Usage: 
help                        Display this help text
instance                    Modify instances, or set current instance
manage                      Add or remove files or folders from the pack
run                         Start migration process

For more help, type the command you want, then 'help'"""

    print(syntax)
    while True:
        args = shell_input(settings.instance)

        settings.write_to_json()
