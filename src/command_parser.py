import sys
from collections.abc import Callable
from inspect import Parameter, Signature, signature
from pathlib import Path
from typing import Any, NamedTuple

import str_templates
from classes import CommandNotExist
from commandtrie import TrieNode, build_command_trie
from helpers import shell_input
from settings import Settings


class ResolvedCommand(NamedTuple):
    fn: Callable
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
    if node.fn is None:
        raise CommandNotExist(str_templates.ERR_COMMAND_NONEXISTENT.format(cmd_path))
    args = tokens[args_starting_index:]

    return ResolvedCommand(
        node.fn, args, node.help, node.preprocessor_fn, node.preprocessor_args
    )


def execute_command(cmd: ResolvedCommand) -> None:
    processed_args = cmd.args
    for preprocessor_fn, preprocessor_args in zip(
        cmd.preprocessor_fn, cmd.preprocessor_args
    ):
        processed_args = preprocessor_fn(processed_args, *preprocessor_args)

    cmd.fn(*processed_args)


def get_fn_min_max_positional_args(fn: Callable) -> tuple[int, int | None]:
    min_args: int = 0
    max_args: int | None = 0

    sig: Signature = signature(fn)

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


def command_parser() -> Settings:
    settings = Settings.from_disk(Path("settings.json"))

    command_trie_root: TrieNode = build_command_trie(settings)
    command: TrieNode = command_trie_root
    while True:
        try:
            tokens = shell_input(settings.instance)

            cmd = get_command(command_trie_root, tokens)
            execute_command(cmd)

            settings.write_to_json()

        except KeyboardInterrupt:
            settings.write_to_json()
            sys.exit(0)
        except (CommandNotExist, ValueError) as e:
            print(e)
        except TypeError as e:
            print(e)
            print(command.help)
    return settings
