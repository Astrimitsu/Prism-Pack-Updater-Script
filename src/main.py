import sys
from pathlib import Path

from f_cli import FoxCLI
from settings import Settings

if sys.version_info < (3, 15, 0):  # noqa: UP036
    print("FATAL: Python v3.15.0 or greater is required to run this program. The program will now exit.")
    input("Press enter to continue. . .")
    sys.exit()


def main() -> None:
    settings = Settings.from_disk(Path("settings.json"))
    cli: FoxCLI = FoxCLI()
    cli.register(settings)
    cli.build()
    cli.run(prompt=lambda: settings.instance)

if __name__ == "__main__":
    main()
