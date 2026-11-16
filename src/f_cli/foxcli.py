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
    """A trie-based command-line interface framework for Python.

    It accepts container classes containing methods decorated with `@command`, 
    and/or classes decorated with `@namespace`.

    The framework supports dynamic registration and deregistration, preprocessor 
    pipelines for raw arguments, and custom argument coercion.

    It can process arguments passed directly (like `sys.argv`), or run 
    interactively by prompting for command input if no arguments are given.
    
    Args:
        *command_objects: Initial command-containing objects or classes to 
            register upon instantiation.

    Attributes:
        coercion_fn: An optional custom callback used to coerce string tokens 
            into target parameter types during argument binding.
            This should return a single coerced object per call, 
            greedily consuming as many tokens from the deque
            as desired. 
            At the moment, only positional arguments are supported.

    Methods:
        register: Adds command objects to the active command trie.
        deregister: Removes command objects from the command trie.
        run: Parses incoming tokens (or shell prompt) and executes the matching command.
    """
    def __init__(self, *command_objects: object) -> None:
        self._trie: TrieNode | None = None
        self.coercion_fn: Callable[[deque[object], Parameter], object] | None = None
        self._registered_objects: set[object] = set()
        self._registered_types: set[type] = set()
        self.register(*command_objects)

    def register(self, *command_objects: object) -> None:
        """Register command-containing objects or classes to the command trie.

        Only one object per type can be registered.
        
        Args:
            *command_objects: Command-containing objects or classes to be registered."""
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
        """Remove command-containing objects or classes from the command trie.

        Args:
            *command_objects: Command-containing objects or classes to be removed."""
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
        """Parse arguments or prompt for input, then route and execute the matching command.

        If explicit `args` are provided, they are processed directly (such as `sys.argv`). 
        Otherwise, an interactive shell prompt is used to gather input. 

        Common CLI errors (such as nonexistent commands, invalid argument counts, or 
        coercion failures) are caught, printed, and accompanied by the command's help text.

        Args:
            prompt: A callable that returns input strings when running interactively.
            args: An optional explicit list of command-line string arguments.

        Returns:
            The return value of the executed command function.
        """
        
        if not self._trie:
            raise ValueError("FoxCLI object contains no registered commands")

        cmd: TrieNode | ResolvedCommand = self._trie

        try:
            if args:
                tokens = clean_input(strip_script_name(args))
            else:
                tokens = clean_input(shell_input(prompt()))

            cmd = self._get_command(tokens)

            bound_args: BoundArguments = process_command_args(cmd, self.coercion_fn)

            command_return: object = cmd.fn(*bound_args.args, **bound_args.kwargs)

            return command_return

        except CommandNotExist as e:
            print(e)
        except (InvalidCommandArgCount, CoercionError) as e:
            print(e)
            print(cmd.help)

    def _get_command(self, tokens: list[str]) -> ResolvedCommand:
        if not self._trie:
            raise ValueError("FoxCLI object contains no registered commands")
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
