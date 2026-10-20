from collections.abc import Callable
from typing import NamedTuple

from settings import Settings


class Command(NamedTuple):
    path: tuple[str, ...]
    preprocessor_fn: tuple[Callable, ...] | None
    preprocessor_args: tuple[tuple, ...] | None
    fn: Callable | None
    help: str


def build_commands(settings: Settings) -> tuple[Command, ...]:
    return (
        Command(
            ("instance",),
            None,
            None,
            settings.get_instances,
            "instance\nDisplay all active instances",
        ),
        Command(
            ("instance", "set"),
            None,
            None,
            settings.set_instance,
            "instance set <alias>\nSet current instance",
        ),
        Command(
            ("instance", "add"),
            None,
            None,
            settings.add_instance,
            "instance add <path> [alias]\nAdds a new instance, alias defaults to folder name if not specified. Path must be surrounded by quotes.",
        ),
        Command(
            ("instance", "remove"),
            None,
            None,
            settings.remove_instance,
            "instance remove <alias>\nRemoves an existing instance"
        )
    )

def add_list_to_command_trie(trie: dict, commands: tuple[Command, ...]):
    command_fields = [f for f in Command._fields if f != "path"]
    for command in commands:
        trie_path = trie
        for command_part in command.path:
            if command_part not in trie_path:
                trie_path[command_part] = {}
            trie_path = trie_path[command_part]
        for key, value in command._asdict().items():
            if key == "path":
                continue
            trie_path[key] = value

def build_command_trie(settings: Settings) -> dict:
    command_trie: dict = {}
    add_list_to_command_trie(command_trie, build_commands(settings))
    return command_trie