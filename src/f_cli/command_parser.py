from collections.abc import Callable
from inspect import Signature
from typing import NamedTuple


class ResolvedCommand(NamedTuple):
    fn: Callable
    fn_sig: Signature
    args: tuple[str, ...]
    kwarg_map: frozendict[str, str]
    help: str
    preprocessor_fn: tuple[Callable, ...]
    preprocessor_args: tuple[tuple, ...]


def run_positional_preprocessors(tokens: list[str], cmd: ResolvedCommand) -> list[str]:
    processed_args: list[str] = tokens.copy()
    for preprocessor_fn, preprocessor_args in zip(
        cmd.preprocessor_fn, cmd.preprocessor_args
    ):
        processed_args = preprocessor_fn(processed_args, *preprocessor_args)
    return processed_args


