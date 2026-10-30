import sys
from collections.abc import Callable, Sequence
from inspect import BoundArguments, Parameter, Signature
from pathlib import Path
from types import UnionType
from typing import Any, NamedTuple, get_args

import error_strings
from classes import CommandNotExist, InvalidCommandArgCount
from commandtrie import TrieNode, build_command_trie
from helpers import shell_input
from settings import Settings


class ResolvedCommand(NamedTuple):
    fn: Callable
    fn_sig: Signature
    args: list[Any]
    help: str
    preprocessor_fn: tuple[Callable, ...]
    preprocessor_args: tuple[tuple, ...]


def get_command(command_trie: TrieNode, tokens: list[str]) -> ResolvedCommand:
    node: TrieNode = command_trie
    args_starting_index: int = 0

    for token in tokens:
        if token not in node.subcommands:
            break
        node = node.subcommands[token]
        args_starting_index += 1

    cmd_path = " ".join(tokens[:args_starting_index])
    if node.fn is None or node.fn_sig is None:
        print(node.fn)
        print(node.fn_sig)
        raise CommandNotExist(error_strings.ERR_COMMAND_NONEXISTENT.format(cmd_path))
    args = tokens[args_starting_index:]

    return ResolvedCommand(
        node.fn,
        node.fn_sig,
        args,
        node.help,
        node.preprocessor_fn,
        node.preprocessor_args,
    )


def execute_command(cmd: ResolvedCommand) -> None:
    pass


def get_fn_min_max_positional_args(sig: Signature) -> tuple[int, int | None]:
    min_args: int = 0
    max_args: int | None = 0

    for param in sig.parameters.values():
        match param.kind:
            case Parameter.POSITIONAL_ONLY | Parameter.POSITIONAL_OR_KEYWORD:
                max_args += 1
            case Parameter.VAR_POSITIONAL:
                max_args = None
                break
            case Parameter.KEYWORD_ONLY | Parameter.VAR_KEYWORD:
                break

        if param.default is Parameter.empty:
            min_args += 1

    return min_args, max_args


def assert_positional_arg_count_within_bounds(
    sig: Signature, args: int | Sequence[Any]
) -> None:
    arg_count = args if isinstance(args, int) else len(args)
    min_args, max_args = get_fn_min_max_positional_args(sig)
    if arg_count < min_args:
        raise InvalidCommandArgCount(error_strings.ERR_INVALID_COMMAND_ARGCOUNT)
    if max_args is not None and max_args < arg_count:
        raise InvalidCommandArgCount(error_strings.ERR_INVALID_COMMAND_ARGCOUNT)


def process_command_args(cmd: ResolvedCommand) -> BoundArguments:
    processed_args = cmd.args.copy()
    for preprocessor_fn, preprocessor_args in zip(
        cmd.preprocessor_fn, cmd.preprocessor_args
    ):
        processed_args = preprocessor_fn(processed_args, *preprocessor_args)

    assert_command_args_within_bounds(cmd.fn_sig, processed_args)

    for i, (arg, param) in enumerate(
        zip(processed_args, cmd.fn_sig.parameters.values())
    ):
        annotation: type | UnionType = param.annotation
        if annotation is Parameter.empty:
            continue
        if isinstance(annotation, UnionType):
            constructor: type = get_args(param.annotation)[0]
        else:
            constructor: type = annotation

        if constructor is str:
            continue
        processed_args[i] = constructor(arg)

    bound_args = cmd.fn_sig.bind(*processed_args)

    return bound_args


def command_parser() -> Settings:
    settings = Settings.from_disk(Path("settings.json"))

    command_trie_root: TrieNode = build_command_trie(settings)
    cmd: TrieNode | ResolvedCommand = command_trie_root
    while True:
        try:
            tokens = shell_input(settings.instance)

            cmd = get_command(command_trie_root, tokens)

            bound_args: BoundArguments = process_command_args(cmd)

            cmd.fn(*bound_args.args, **bound_args.kwargs)

            settings.write_to_json()

        except KeyboardInterrupt:
            settings.write_to_json()
            sys.exit(0)
        except (CommandNotExist, ValueError) as e:
            print(e)
        except InvalidCommandArgCount as e:
            print(e)
            print(cmd.help)
    return settings
