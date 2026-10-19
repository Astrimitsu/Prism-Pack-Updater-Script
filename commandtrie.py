from collections.abc import Callable
from typing import NamedTuple

from Settings import Settings


class Command(NamedTuple):
    path: list[str]
    fn: Callable | None
    help: str


def build_commands(settings: Settings) -> list:
    return [
        Command(
            ["instance"],
            settings.get_instances,
            "instance\nDisplay all active instances",
        ),
        Command(
            ["instance", "set"],
            settings.set_instance,
            "instance set <alias>\nSet current instance",
        ),
        Command(
            ["instance", "add"],
            settings.add_instance,
            "instance add <path> [alias]\nAdds a new instance, alias defaults to folder name if not specified. Path must be surrounded by quotes.",
        ),
        Command(
            ["instance", "remove"],
            settings.remove_instance,
            "instance remove <alias>\nRemoves an existing instance"
        )
    ]

def add_list_to_command_trie(trie: dict, commands: list):
    for command in commands:
        tree_path = trie
        for command_part in command.path:
            if command_part not in tree_path:
                tree_path[command_part] = {}
            tree_path = tree_path[command_part]
        tree_path["fn"] = command.fn
        tree_path["help"] = command.help

def build_command_trie(settings: Settings) -> dict:
    command_trie: dict = {}
    add_list_to_command_trie(command_trie, build_commands(settings))
    return command_trie