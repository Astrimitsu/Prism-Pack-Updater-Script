from collections.abc import Sequence
from inspect import BoundArguments, Parameter, Signature
from types import UnionType
from typing import get_args

import error_strings
from classes import InvalidCommandArgCount
from consts import ANY_KWARGS


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


def get_function_kwargs(sig: Signature) -> dict[object, object]:
    kwargs: dict[object, object] = {}
    for param_name, param in sig.parameters.items():
        if param.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY):
            kwargs[param_name] = param.default
        elif param.kind is Parameter.VAR_KEYWORD:
            kwargs[ANY_KWARGS] = param.default
    return kwargs


def assert_positional_arg_count_within_bounds(sig: Signature, args: Sequence) -> None:
    arg_count: int = len(args)
    min_args, max_args = get_fn_min_max_positional_args(sig)
    if arg_count < min_args:
        raise InvalidCommandArgCount(error_strings.ERR_INVALID_COMMAND_ARGCOUNT)
    if max_args is not None and max_args < arg_count:
        raise InvalidCommandArgCount(error_strings.ERR_INVALID_COMMAND_ARGCOUNT)


def typecast_bound_args(bound_args: BoundArguments) -> BoundArguments:
    cast_args = {
        name: typecast_arg_from_param(arg, bound_args.signature.parameters[name])
        for name, arg in bound_args.arguments.items()
    }
    return BoundArguments(bound_args.signature, cast_args)


def typecast_arg_from_param(arg: object, param: Parameter) -> object:
    annotation: type | UnionType = param.annotation
    if annotation is Parameter.empty:
        return arg

    if isinstance(annotation, UnionType):
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
