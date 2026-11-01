from collections.abc import Callable
from inspect import BoundArguments, Signature
from typing import Any, NamedTuple

import error_strings
from classes import CommandNotExist, CommandSignal, InvalidCommandArgCount
from commandtrie import TrieNode
from helpers import shell_input
from sig_tools import assert_positional_arg_count_within_bounds, typecast_command_arg_from_param


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


def command_parser(command_trie_root: TrieNode, *, prompt: Callable | None = None ) -> object:
    cmd: TrieNode | ResolvedCommand = command_trie_root

    try:
        tokens = shell_input(prompt() if prompt else None)

        cmd = get_command(command_trie_root, tokens)

        bound_args: BoundArguments = process_command_args(cmd)

        command_return: CommandSignal = cmd.fn(
            *bound_args.args, **bound_args.kwargs
        )

        return command_return

    except (CommandNotExist, ValueError) as e:
        print(e)
    except InvalidCommandArgCount as e:
        print(e)
        print(cmd.help)