from collections import deque
from collections.abc import Callable
from inspect import BoundArguments, Parameter
from math import isfinite
from types import UnionType
from typing import get_args

import f_cli.error_strings as err

from . import consts
from .command_parser import ResolvedCommand, run_positional_preprocessors
from .exception_classes import CoercionError, InvalidCommandArgCount
from .kwarg_extractor import extract_kwargs_from_args
from .sig_utils import assert_positional_arg_count_within_bounds


def coerce_arg_from_param(arg: object, param: Parameter) -> object:
    if param.annotation is Parameter.empty:
        return arg

    annotations: tuple[type, ...] = get_param_types(param.annotation)
    default_constructor: type = annotations[0]

    coerced_arg: object = arg

    if isinstance(arg, str):
        coerced_arg = coerce_string_to_obj(arg, default_constructor)

    if isinstance(coerced_arg, annotations):
        return coerced_arg

    return default_constructor(coerced_arg)


def get_param_types(annotation: type | UnionType) -> tuple[type, ...]:
    if isinstance(annotation, UnionType):
        return get_args(annotation)
    return (annotation,)


def str_to_int(string: str) -> int:
    try:
        number: int = int(string)
    except ValueError:
        raise CoercionError(err.ERR_NOT_A_NUMBER.format(string))
    return number


def str_to_float(string: str) -> float:
    try:
        number: float = float(string)
        if not isfinite(number):
            raise ValueError
    except ValueError:
        raise CoercionError(err.ERR_NOT_A_NUMBER.format(string))
    return number


def str_to_bool(string: str) -> bool:
    if string in consts.truthy_strings:
        return True
    if string in consts.falsy_strings:
        return False
    raise CoercionError(err.ERR_STR_NOT_TRUE_OR_FALSE.format(string))


_COERCION_REGISTRY: frozendict = frozendict(
    {
        int: str_to_int,
        float: str_to_float,
        bool: str_to_bool,
    }
)


def coerce_string_to_obj(token: str, constructor: type) -> object:
    coercer: Callable | None = _COERCION_REGISTRY.get(constructor)
    if coercer:
        return coercer(token)
    return token


def coerce_bound_args(bound_args: BoundArguments) -> BoundArguments:
    cast_args: dict[str, object] = {}

    for arg_name, arg in bound_args.arguments.items():
        param: Parameter = bound_args.signature.parameters[arg_name]
        cast_args[arg_name] = coerce_arg_from_param(arg, param)

    return BoundArguments(bound_args.signature, cast_args)


def run_user_coercion(
    args: list[str], cmd: ResolvedCommand, user_coercion: Callable
) -> list[object]:
    token_stream: deque = deque(args)
    coerced_args: list[object] = []
    try:
        for param in cmd.fn_sig.parameters.values():
            if not token_stream:
                break
            coerced_args.append(user_coercion(param, token_stream))
    except IndexError:
        raise InvalidCommandArgCount(err.ERR_INVALID_COMMAND_ARGCOUNT)

    return coerced_args


def process_command_args(
    cmd: ResolvedCommand,
    user_coercion: Callable[[deque[object], Parameter], object] | None,
) -> BoundArguments:
    args, kwargs = extract_kwargs_from_args(cmd.args, cmd.fn_sig, cmd.kwarg_map)

    processed_args = run_positional_preprocessors(args, cmd)

    coerced_args = (
        run_user_coercion(processed_args, cmd, user_coercion)
        if user_coercion
        else processed_args
    )

    assert_positional_arg_count_within_bounds(cmd.fn_sig, coerced_args)

    cast_args = coerce_bound_args(cmd.fn_sig.bind(*coerced_args, **kwargs))

    return cast_args
