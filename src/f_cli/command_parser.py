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


def run_positional_preprocessors(tokens: list[str], cmd: ResolvedCommand) -> list[str]:
    processed_args: list[str] = tokens.copy()
    for preprocessor_fn in cmd.preprocessor_fn:
        processed_args = preprocessor_fn(processed_args)
    return processed_args
