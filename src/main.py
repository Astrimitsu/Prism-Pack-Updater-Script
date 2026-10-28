import sys

from config import command_parser
from file_manager import file_manager
from settings import Settings

if sys.version_info < (3, 15, 0):  # noqa: UP036
    print("FATAL: Python v3.15.0 or greater is required to run this program. The program will now exit.")
    input("Press enter to continue. . .")
    sys.exit()


def main() -> None:
    settings: Settings = command_parser()
    file_manager(settings)


if __name__ == "__main__":
    main()
