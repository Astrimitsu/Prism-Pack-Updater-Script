import sys

from classes import Settings
from config import config
from file_manager import file_manager

if sys.version_info < (3, 14, 0):  # noqa: UP036
    print("FATAL: Python v3.14.0 or greater is required to run this program. The program will now exit.")
    input("Press enter to continue. . .")
    sys.exit()


def main() -> None:
    settings: Settings = config()
    file_manager(settings)


if __name__ == "__main__":
    main()
