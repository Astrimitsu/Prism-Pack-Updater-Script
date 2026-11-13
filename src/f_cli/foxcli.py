from collections import deque
from collections.abc import Callable
from inspect import BoundArguments, Parameter

import error_strings as errstr

from .coercion import process_command_args
from .command_parser import ResolvedCommand
from .commandtrie import TrieNode, build_command_trie
from .exception_classes import CoercionError, CommandNotExist, InvalidCommandArgCount
from .shell_utils import clean_input, shell_input, strip_script_name


class FoxCLI:
    def __init__(self, *command_objects: object) -> None:
        self._trie: TrieNode | None = None
        self.coercion_fn: Callable[[deque[object], Parameter], object] | None = None
        self._registered_objects: set[object] = set()
        self._registered_types: set[type] = set()
        self.register(*command_objects)

    def register(self, *command_objects: object) -> None:
        for obj in command_objects:
            if obj in self._registered_objects:
                continue
            if type(obj) in self._registered_types:
                raise ValueError(
                    errstr.ERR_OBJECT_ALREADY_REGISTERED.format(type(obj).__name__)
                )
            
        for obj in command_objects:
            self._registered_objects.add(obj)
            self._registered_types.add(type(obj))
        self._rebuild_trie()

    def deregister(self, *command_objects: object) -> None:
        for obj in command_objects:
            if obj not in self._registered_objects:
                continue

            self._registered_objects.remove(obj)
            self._registered_types.remove(type(obj))
        self._rebuild_trie()

    def _rebuild_trie(self) -> None:
        self._trie = build_command_trie(self._registered_objects)

    def run(
        self, *, prompt: Callable = lambda: None, args: list[str] | None = None
    ) -> object:

        if not self._trie:
            raise ValueError()

        cmd: TrieNode | ResolvedCommand = self._trie

        try:
            if args:
                tokens = clean_input(strip_script_name(args))
            else:
                tokens = clean_input(shell_input(prompt()))

            cmd = self.get_command(tokens)

            bound_args: BoundArguments = process_command_args(cmd, self.coercion_fn)

            command_return: object = cmd.fn(*bound_args.args, **bound_args.kwargs)

            return command_return

        except CommandNotExist as e:
            print(e)
        except (InvalidCommandArgCount, CoercionError) as e:
            print(e)
            print(cmd.help)

    def get_command(self, tokens: list[str]) -> ResolvedCommand:
        if not self._trie:
            raise ValueError("Trie not initialized")
        node: TrieNode = self._trie
        args_starting_index: int = 0

        for token in tokens:
            if token not in node.subcommands:
                break
            node = node.subcommands[token]
            args_starting_index += 1

        if node.fn is None or node.fn_sig is None:
            cmd_path = " ".join(tokens[:args_starting_index])
            raise CommandNotExist(errstr.ERR_COMMAND_NONEXISTENT.format(cmd_path))

        args = tuple(tokens[args_starting_index:])

        return ResolvedCommand(
            node.fn,
            node.fn_sig,
            args,
            node.kwarg_map,
            node.help,
            node.preprocessor_fn,
            node.preprocessor_args,
        )
