from collections.abc import Callable
from inspect import BoundArguments, Signature
from typing import NamedTuple

import error_strings
from classes import (
    CommandNotExist,
    CommandSignal,
    InvalidCommandArgCount,
)
from commandtrie import TrieNode
from helpers import shell_input
from sig_tools import (
    assert_positional_arg_count_within_bounds,
    typecast_bound_args,
)
from kwarg_extractor import extract_kwargs_from_args


class ResolvedCommand(NamedTuple):
    fn: Callable
    fn_sig: Signature
    args: tuple[str, ...]
    kwarg_map: frozendict[str, str]
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


def run_positional_preprocessors(tokens: list[str], cmd: ResolvedCommand) -> list[str]:
    processed_args: list[str] = tokens.copy()
    for preprocessor_fn, preprocessor_args in zip(
        cmd.preprocessor_fn, cmd.preprocessor_args
    ):
        processed_args = preprocessor_fn(processed_args, *preprocessor_args)
    return processed_args


def process_command_args(cmd: ResolvedCommand) -> BoundArguments:
    args, kwargs = extract_kwargs_from_args(cmd.args, cmd.fn_sig, cmd.kwarg_map)

    processed_args = run_positional_preprocessors(args, cmd)
    
    assert_positional_arg_count_within_bounds(cmd.fn_sig, processed_args)

    cast_args = typecast_bound_args(cmd.fn_sig.bind(*processed_args, **kwargs))

    return cast_args


def command_parser(
    command_trie_root: TrieNode, *, prompt: Callable | None = None
) -> object:
    cmd: TrieNode | ResolvedCommand = command_trie_root

    try:
        tokens = shell_input(prompt() if prompt else None)

        cmd = get_command(command_trie_root, tokens)

        bound_args: BoundArguments = process_command_args(cmd)

        command_return: CommandSignal = cmd.fn(*bound_args.args, **bound_args.kwargs)

        return command_return

    except (CommandNotExist, ValueError) as e:
        print(e)
    except InvalidCommandArgCount as e:
        print(e)
        print(cmd.help)
