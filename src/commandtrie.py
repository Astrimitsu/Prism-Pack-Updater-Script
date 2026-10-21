from collections import defaultdict
from collections.abc import Callable, Iterator
from typing import Any, NamedTuple

from settings import Settings


class Command(NamedTuple):
    path: tuple[str, ...]
    preprocessor_fn: tuple[Callable, ...] | None
    preprocessor_args: tuple[tuple, ...] | None
    fn: Callable | None
    help: str

    def trienode_properties(self) -> Iterator[tuple[str, Any]]:
        yield from ((k, v) for k, v in self._asdict().items() if k != "path")


class TrieNode:
    def __init__(
        self,
        preprocessor_fn: tuple[Callable, ...] | None = None,
        preprocessor_args: tuple[tuple, ...] | None = None,
        fn: Callable | None = None,
        help: str | None = None,
    ) -> None:
        self.subcommands: defaultdict[str, TrieNode] | None = None
        self.preprocessor_fn: tuple[Callable, ...] | None = preprocessor_fn
        self.preprocessor_args: tuple[tuple, ...] | None = preprocessor_args
        self.fn: Callable | None = fn
        self.help: str | None = help

    def add_command_to_trie(self, command: Command) -> None:
        current: TrieNode = self
        for command_part in command.path:
            if current.subcommands is None:
                current.subcommands = defaultdict(TrieNode)
            current = current.subcommands[command_part]
        for k, v in command.trienode_properties():
            setattr(current, k, v)


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
            "instance remove <alias>\nRemoves an existing instance",
        ),
    )

def build_command_trie(settings: Settings) -> TrieNode:
    command_trie: TrieNode = TrieNode()
    for command in build_commands(settings):
        command_trie.add_command_to_trie(command)
    return command_trie
