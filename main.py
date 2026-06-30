from classes import Settings
from config import config
from file_manager import file_manager
import sys


if not sys.version_info.major > 3 or sys.version_info.minor >= 14:
    print("FATAL: Python v3.14.0 or greater is required to run this program. The program will now exit.")
    input("Press enter to continue. . .")


def main() -> None:
    settings: Settings = config()
    file_manager(settings)


if __name__ == "__main__":
    main()
