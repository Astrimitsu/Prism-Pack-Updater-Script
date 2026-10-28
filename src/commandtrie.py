import sys
from collections import defaultdict
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any

from settings import Settings


@dataclass(frozen=True)
class Command:
    path: tuple[str, ...]
    fn: Callable | None = None
    help: str = ""
    preprocessor_fn: tuple[Callable, ...] = field(default_factory=tuple)
    preprocessor_args: tuple[tuple, ...] = field(default_factory=tuple)

    def trienode_properties(self) -> Iterator[tuple[str, Any]]:
        yield from ((k, v) for k, v in vars(self).items() if k != "path")


class TrieNode:
    def __init__(
        self,
        fn: Callable | None = None,
        help: str = "",
        preprocessor_fn: tuple[Callable, ...] | None = None,
        preprocessor_args: tuple[tuple, ...] | None = None,
    ) -> None:
        self.subcommands: defaultdict[str, TrieNode] | frozendict[str, TrieNode] = (
            defaultdict(TrieNode)
        )
        self.fn: Callable | None = fn
        self.help: str | None = help
        self.preprocessor_fn: tuple[Callable, ...] = (
            preprocessor_fn if preprocessor_fn else ()
        )
        self.preprocessor_args: tuple[tuple[Any], ...] = (
            preprocessor_args if preprocessor_args else ()
        )
        self._frozen = False

    def add_command_to_trie(self, command: Command) -> None:
        current: TrieNode = self
        for command_part in command.path:
            current = current.subcommands[command_part]
        for k, v in command.trienode_properties():
            setattr(current, k, v)

    def _deepfreeze(self) -> None:
        for node in self.subcommands.values():
            node._deepfreeze()
        self.subcommands = frozendict(self.subcommands)
        self._frozen = True

    def __setattr__(self, key, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(f"Cannot modify frozen {self.__class__.__name__}")
        super().__setattr__(key, value)

    def __delattr__(self, name: str) -> None:
        if getattr(self, "_frozen", False):
            raise AttributeError(f"Cannot modify frozen {self.__class__.__name__}")
        super().__delattr__(name)


def build_commands(settings: Settings) -> tuple[Command, ...]:
    return (
        Command(("quit",), lambda *args: sys.exit(0), "Exit the program"),
        Command(
            ("instance",),
            settings.get_instances,
            "instance\nDisplay all active instances",
        ),
        Command(
            ("instance", "set"),
            settings.set_instance,
            "instance set <alias>\nSet current instance",
        ),
        Command(
            ("instance", "add"),
            settings.add_instance,
            "instance add <path> [alias]\nAdds a new instance, alias defaults to folder name if not specified. Path must be surrounded by quotes.",
        ),
        Command(
            ("instance", "remove"),
            settings.remove_instance,
            "instance remove <alias>\nRemoves an existing instance",
        ),
    )


def trie_from_commands(commands: list[Command]) -> TrieNode:
    trie: TrieNode = TrieNode()
    for command in commands:
        trie.add_command_to_trie(command)
    return trie


def build_command_trie(settings: Settings) -> TrieNode:
    commands: list[Command] = []
    commands.extend(build_commands(settings))
    trie = trie_from_commands(commands)
    trie._deepfreeze()
    return trie
