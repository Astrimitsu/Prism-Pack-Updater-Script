from collections import defaultdict
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field, replace
from functools import partial, partialmethod
from inspect import Signature, getdoc, getmembers_static, signature
from typing import Any


@dataclass(frozen=True)
class CommandMetadata:
    path: tuple[str, ...]
    desc: str | None
    help: str | None
    kwarg_map: frozendict[str, str] = field(default_factory=frozendict)
    preprocessor_fn: tuple[Callable[[list[Any]], list[Any]], ...] = field(
        default_factory=tuple
    )

    def trienode_properties(self) -> Iterator[tuple[str, object]]:
        yield from ((k, v) for k, v in vars(self).items() if k != "path")


command_registry: dict[Callable, CommandMetadata] = {}


class TrieNode:
    def __init__(
        self,
        fn: Callable | None = None,
        desc: str | None = None,
        help: str | None = None,
        kwarg_map: frozendict[str, str] = frozendict(),
        preprocessor_fn: tuple[Callable, ...] | None = None,
    ) -> None:
        self.subcommands: defaultdict[str, TrieNode] | frozendict[str, TrieNode] = (
            defaultdict(TrieNode)
        )
        self.fn: Callable | None = fn
        self.fn_sig: Signature | None = signature(fn) if fn else None
        self.kwarg_map: frozendict[str, str] = kwarg_map
        self.desc: str | None = desc
        self.help: str | None = help
        self.preprocessor_fn: tuple[Callable, ...] = (
            preprocessor_fn if preprocessor_fn else ()
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


def _parse_helptext(
    obj: object, desc: str | None, help: str | None
) -> tuple[str | None, str | None]:
    text: str | None = help or getdoc(obj)
    if not text:
        return desc or None, None

    cmd_desc: str | None = desc or text.split("\n")[0]
    cmd_help: str | None = text

    return cmd_desc, cmd_help


def namespace(
    path: Sequence[str], *, desc: str | None = None, help: str | None = None
) -> Callable:
    """Defines a command namespace for a container class.

    The decorated class is added to an internal command registry,
    prepending all commands within the class with the specified path.

    Note: Using a namespace is optional; container classes can be
    registered without one.

    Args:
        path: A sequence of strings, with each index representing a subcommand.
        desc: A short description of the command.
          Pulled from docstring if not provided, if the class has one.
        help: Help text to be associated with the namespace.
          Pulled from docstring if not provided, if the class has one.

    """

    def decorator(cls: type):
        if cls in command_registry:
            raise ValueError(f"Class {cls.__name__} is already registered")

        cmd_desc, cmd_help = _parse_helptext(cls, desc, help)
        metadata: CommandMetadata = CommandMetadata(tuple(path), cmd_desc, cmd_help)
        command_registry[cls] = metadata
        return cls

    return decorator

type FunctionOrDescriptor = Callable[..., Any] | classmethod[Any, Any, Any] | staticmethod[Any, Any]

def command[F: FunctionOrDescriptor](
    path: Sequence[str],
    *,
    desc: str | None = None,
    help: str | None = None,
    kwarg_map: Mapping[str, str] = frozendict(),
    preprocessor_fn: Sequence[Callable[[list[Any]], list[Any]]] = (),
) -> Callable[[F], F]:
    """Registers a function as a CLI command.

    The decorated callable is added to an internal command registry.
    Classes, instances of, or modules containing these methods can then be passed to a
    FoxCLI object to build the command trie.

    Args:
        path: A sequence of strings, where each element represents a subcommand level.
        desc: A short description of the command.
          Pulled from docstring if not provided, if the function has one.
        help: Help text to be associated with the command.
          Pulled from docstring if not provided, if the function has one.
        kwarg_map: Optional mapping to translate CLI flags to keyword arguments.
            If omitted, flags match keyword argument names exactly.
        preprocessor_fn: A sequence of callables that modify the raw input
            arguments before parsing, returning the updated list.
    """

    def decorator(fn: F) -> F:

        unwrapped = _unwrap_function(fn)
        if unwrapped in command_registry:
            raise ValueError(f"Function {unwrapped!r} is already registered")
        
        cmd_desc, cmd_help = _parse_helptext(fn, desc, help)

        metadata: CommandMetadata = CommandMetadata(
            tuple(path),
            cmd_desc,
            cmd_help,
            frozendict(kwarg_map),
            tuple(preprocessor_fn),
        )

        command_registry[unwrapped] = metadata
        return fn

    return decorator


def contains_command(fn: Callable) -> bool:
    return _unwrap_function(fn) in command_registry


def _unwrap_function(fn: FunctionOrDescriptor) -> Callable:
    """(Hopefully) cleanly handles functions inside of descriptor objects
    (ie: @classmethod, @staticmethod) to extract the function inside."""
    unwrapped: Any = fn
    seen = set()

    while True:
        if id(unwrapped) in seen:
            raise ValueError(f"Circular reference detected while unwrapping {fn!r}")
        seen.add(id(unwrapped))

        if hasattr(unwrapped, "__func__"):
            unwrapped = unwrapped.__func__
        elif hasattr(unwrapped, "__wrapped__"):
            unwrapped = unwrapped.__wrapped__
        elif isinstance(unwrapped, (partial, partialmethod)):
            unwrapped = unwrapped.func
        else:
            break

    return unwrapped


def _bind_method(fn: Callable, owner: Any):
    return fn if isinstance(owner, type) else fn.__get__(owner, type(owner))


def build_command_trie(command_containers: set[Any]) -> TrieNode:
    trie_root: TrieNode = TrieNode()
    for container in command_containers:
        _process_container(container, trie_root)
        _process_container_functions(container, trie_root)

    trie_root._deepfreeze()

    return trie_root


def _process_container(container: Any, trie_root: TrieNode) -> None:
    if container in command_registry:
        trie_root.add_command_to_trie(None, command_registry[container])


def _process_container_functions(container: Any, trie_root: TrieNode) -> None:
    for _, member in getmembers_static(container, predicate=contains_command):
        fn: Callable = _unwrap_function(member)

        metadata: CommandMetadata = command_registry[fn]

        bound_fn = _bind_method(member, container)

        if container in command_registry:
            container_metadata: CommandMetadata = command_registry[container]
            metadata = replace(metadata, path=container_metadata.path + metadata.path)

        trie_root.add_command_to_trie(bound_fn, metadata)
