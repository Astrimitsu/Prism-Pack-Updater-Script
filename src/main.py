import sys
from pathlib import Path

from command_parser import command_parser
from commandtrie import TrieNode, build_command_trie
from file_manager import file_manager
from settings import Settings
from system_commands import SystemCommands

if sys.version_info < (3, 15, 0):  # noqa: UP036
    print("FATAL: Python v3.15.0 or greater is required to run this program. The program will now exit.")
    input("Press enter to continue. . .")
    sys.exit()


def main() -> None:
    settings = Settings.from_disk(Path("settings.json"))
    commands: TrieNode = build_command_trie(settings, SystemCommands)
    command_parser(commands, prompt=lambda: settings.instance)
    file_manager(settings)


if __name__ == "__main__":
    main()
