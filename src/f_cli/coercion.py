from collections import deque
from collections.abc import Callable
from inspect import BoundArguments, Parameter
from types import UnionType
from typing import get_args

from f_cli.command_parser import ResolvedCommand, run_positional_preprocessors
from f_cli.kwarg_extractor import extract_kwargs_from_args
from f_cli.sig_utils import assert_positional_arg_count_within_bounds


def coerce_arg_from_param(arg: object, param: Parameter) -> object:
    if param.annotation is Parameter.empty:
        return arg

    annotation: tuple[type, ...] = get_param_types(param.annotation)

    if isinstance(arg, annotation):
        return arg

    default_constructor: type = annotation[0]
    return default_constructor(arg)


def get_param_types(annotation: type | UnionType) -> tuple[type, ...]:
    if isinstance(annotation, UnionType):
        return get_args(annotation)
    else:
        return (annotation,)


def coerce_bound_args(
    bound_args: BoundArguments, user_coercion: Callable
) -> BoundArguments:
    cast_args: dict[str, object] = {}

    for arg_name, arg in bound_args.arguments.items():
        param: Parameter = bound_args.signature.parameters[arg_name]
        cast_args[arg_name] = coerce_arg_from_param(arg, param)

    return BoundArguments(bound_args.signature, cast_args)


def run_user_coercion(
    args: list[str], cmd: ResolvedCommand, user_coercion: Callable
):
    token_stream: deque = deque(args)
    coerced_args: list[object] = []

    for param in cmd.fn_sig.parameters.values():
        if not token_stream:
            break
        coerced_args.append(user_coercion(param, token_stream))


def process_command_args(
    cmd: ResolvedCommand, user_coercion: Callable
) -> BoundArguments:
    args, kwargs = extract_kwargs_from_args(cmd.args, cmd.fn_sig, cmd.kwarg_map)

    processed_args = run_positional_preprocessors(args, cmd)

    run_user_coercion(processed_args, cmd, user_coercion)

    assert_positional_arg_count_within_bounds(cmd.fn_sig, processed_args)

    cast_args = coerce_bound_args(
        cmd.fn_sig.bind(*processed_args, **kwargs), user_coercion
    )

    return cast_args
