from collections import defaultdict
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field, replace
from inspect import Signature, getmembers_static, isfunction, ismethod, signature
from typing import Any, Protocol


@dataclass(frozen=True)
class CommandMetadata:
    path: tuple[str, ...]
    help: str = ""
    kwarg_map: frozendict[str, str] = field(default_factory=frozendict)
    preprocessor_fn: tuple[Callable, ...] = field(default_factory=tuple)
    preprocessor_args: tuple[tuple[object, ...], ...] = field(default_factory=tuple)

    def trienode_properties(self) -> Iterator[tuple[str, object]]:
        yield from ((k, v) for k, v in vars(self).items() if k != "path")


class TrieNode:
    def __init__(
        self,
        fn: Callable | None = None,
        help: str = "",
        kwarg_map: frozendict[str, str] = frozendict(),
        preprocessor_fn: tuple[Callable, ...] | None = None,
        preprocessor_args: tuple[tuple, ...] | None = None,
    ) -> None:
        self.subcommands: defaultdict[str, TrieNode] | frozendict[str, TrieNode] = (
            defaultdict(TrieNode)
        )
        self.fn: Callable | None = fn
        self.fn_sig: Signature | None = signature(fn) if fn else None
        self.kwarg_map: frozendict[str, str] = kwarg_map
        self.help: str = help
        self.preprocessor_fn: tuple[Callable, ...] = (
            preprocessor_fn if preprocessor_fn else ()
        )
        self.preprocessor_args: tuple[tuple[Any], ...] = (
            preprocessor_args if preprocessor_args else ()
        )
        self._frozen = False

    def add_command_to_trie(
        self, fn: Callable | None, metadata: CommandMetadata
    ) -> None:
        current: TrieNode = self
        for command_part in metadata.path:
            current = current.subcommands[command_part]
        for k, v in metadata.trienode_properties():
            setattr(current, k, v)
        current.fn = fn
        current.fn_sig = signature(fn) if fn else None

    def _deepfreeze(self) -> None:
        for node in self.subcommands.values():
            node._deepfreeze()
        self.subcommands = frozendict(self.subcommands)
        self._frozen = True

    def __setattr__(self, key, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(f"Cannot modify frozen {self.__class__.__name__}")
        object.__setattr__(self, key, value)

    def __delattr__(self, name: str) -> None:
        if getattr(self, "_frozen", False):
            raise AttributeError(f"Cannot modify frozen {self.__class__.__name__}")
        object.__delattr__(self, name)


def namespace(path: Sequence[str], help: str = "") -> Callable:
    """Defines a command namespace for a container class.

    The decorated class is stamped with a _foxcli_command_metadata property,
    prepending all commands within the class with the specified path.

    Note: Using a namespace is optional; container classes can be
    registered without one.

    Args:
        path: A sequence of strings, with each index representing a subcommand.
        help: Help text to be associated with the namespace.
    """

    def decorator(cls: type):
        metadata: CommandMetadata = CommandMetadata(tuple(path), help)
        cls._foxcli_command_metadata = metadata
        return cls

    return decorator

class PreprocessorFN(Protocol):
    def __call__(self, args_to_process: list[Any], *args: object) -> list[object]: ...

def command(
    path: Sequence[str],
    help: str = "",
    kwarg_map: Mapping[str, str] = frozendict(),
    preprocessor_fn: Sequence[PreprocessorFN] = (),
    preprocessor_args: Sequence[Sequence[object]] = (),
) -> Callable:
    """Registers a method as a CLI command.

    The decorated callable is stamped with a _foxcli_command_metadata property.
    Container classes containing these methods can then be passed to a
    FoxCLI object to build the command trie.

    Note: All decorated methods must live inside a container class;
    module-level loose functions are unsupported.

    Args:
        path: A sequence of strings, where each element represents a subcommand level.
        help: Help text to be associated with the command.
        kwarg_map: Optional mapping to translate CLI flags to keyword arguments.
            If omitted, flags match keyword argument names exactly.
        preprocessor_fn: A sequence of callables that modify the raw input
            arguments before parsing, returning the updated list.
        preprocessor_args: A sequence of argument sequences, where each
            subsequence corresponds to the arguments passed to its respective preprocessor.
    """

    def decorator(fn: Callable) -> Callable:
        metadata: CommandMetadata = CommandMetadata(
            tuple(path),
            help,
            frozendict(kwarg_map),
            tuple(preprocessor_fn),
            tuple(tuple(fn_args) for fn_args in preprocessor_args),
        )
        fn._foxcli_command_metadata = metadata  # type: ignore[attr-defined]
        return fn

    return decorator


def build_command_trie(command_containers: set[Any]) -> TrieNode:
    trie_root: TrieNode = TrieNode()
    for container in command_containers:
        container_namespace: CommandMetadata | None = None

        if hasattr(container, "_foxcli_command_metadata"):
            container_namespace = container._foxcli_command_metadata
            trie_root.add_command_to_trie(None, container._foxcli_command_metadata)

        for _, member in getmembers_static(
            container, predicate=lambda m: isfunction(m) or ismethod(m)
        ):
            if hasattr(member, "_foxcli_command_metadata"):
                metadata: CommandMetadata = member._foxcli_command_metadata

                if container_namespace:
                    metadata = replace(
                        metadata, path=container_namespace.path + metadata.path
                    )
                trie_root.add_command_to_trie(member, metadata)

    trie_root._deepfreeze()

    return trie_root
