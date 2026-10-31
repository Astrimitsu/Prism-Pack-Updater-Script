import sys
from collections.abc import Callable
from inspect import BoundArguments, Parameter, Signature
from pathlib import Path
from types import UnionType
from typing import Any, NamedTuple, get_args

import error_strings
from classes import CommandNotExist, InvalidCommandArgCount
from commandtrie import TrieNode, build_command_trie
from helpers import shell_input
from settings import Settings
from sig_tools import assert_positional_arg_count_within_bounds


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


def typecast_command_arg_from_param(arg: object, param: Parameter) -> object:
    annotation: type | UnionType = param.annotation
    if annotation is Parameter.empty:
        return arg

    if annotation is UnionType:
        union: tuple[type, ...] = get_args(param.annotation)
        if type(arg) in union:
            return arg
        constructor: type = get_args(param.annotation)[0]

    else:
        if type(arg) is annotation:
            return arg
        constructor: type = annotation

    if constructor is str:
        return arg
    return constructor(arg)


def process_command_args(cmd: ResolvedCommand) -> BoundArguments:
    processed_args = cmd.args.copy()
    for preprocessor_fn, preprocessor_args in zip(
        cmd.preprocessor_fn, cmd.preprocessor_args
    ):
        processed_args = preprocessor_fn(processed_args, *preprocessor_args)

    assert_positional_arg_count_within_bounds(cmd.fn_sig, processed_args)

    processed_args = [
        typecast_command_arg_from_param(arg, param)
        for arg, param in zip(processed_args, cmd.fn_sig.parameters.values())
    ]

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
