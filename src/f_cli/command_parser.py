from collections.abc import Callable
from inspect import BoundArguments, Signature
from typing import NamedTuple

import error_strings
from commandtrie import TrieNode
from exception_classes import CommandNotExist, InvalidCommandArgCount
from f_cli.typecaster import typecast_bound_args
from kwarg_extractor import extract_kwargs_from_args
from shell_utils import clean_input, shell_input, strip_script_name

from f_cli.sig_utils import (
    assert_positional_arg_count_within_bounds,
)


class ResolvedCommand(NamedTuple):
    fn: Callable
    fn_sig: Signature
    args: tuple[str, ...]
    kwarg_map: frozendict[str, str]
    help: str
    preprocessor_fn: tuple[Callable, ...]
    preprocessor_args: tuple[tuple, ...]


def command_parser(
    command_trie_root: TrieNode,
    *,
    prompt: Callable = lambda: None,
    args: list[str] | None = None
) -> object:

    cmd: TrieNode | ResolvedCommand = command_trie_root

    try:
        if args:
            tokens = clean_input(strip_script_name(args))
        else:
            tokens = clean_input(shell_input(prompt()))

        cmd = get_command(command_trie_root, tokens)

        bound_args: BoundArguments = process_command_args(cmd)

        command_return: object = cmd.fn(*bound_args.args, **bound_args.kwargs)

        return command_return

    except (CommandNotExist, ValueError) as e:
        print(e)
    except InvalidCommandArgCount as e:
        print(e)
        print(cmd.help)


def get_command(command_trie: TrieNode, tokens: list[str]) -> ResolvedCommand:
    node: TrieNode = command_trie
    args_starting_index: int = 0

    for token in tokens:
        if token not in node.subcommands:
            break
        node = node.subcommands[token]
        args_starting_index += 1

    if node.fn is None or node.fn_sig is None:
        cmd_path = " ".join(tokens[:args_starting_index])
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
