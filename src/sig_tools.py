from collections.abc import Sequence
from inspect import Parameter, Signature

import error_strings
from classes import InvalidCommandArgCount
from typing import Any


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


