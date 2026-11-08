from inspect import BoundArguments, Parameter
from types import UnionType
from typing import get_args

from f_cli.command_parser import ResolvedCommand, run_positional_preprocessors
from f_cli.kwarg_extractor import extract_kwargs_from_args
from f_cli.sig_utils import assert_positional_arg_count_within_bounds


def coerce_arg_from_param(arg: object, param: Parameter) -> object:
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


def coerce_bound_args(bound_args: BoundArguments) -> BoundArguments:
    cast_args = {
        name: coerce_arg_from_param(arg, bound_args.signature.parameters[name])
        for name, arg in bound_args.arguments.items()
    }
    return BoundArguments(bound_args.signature, cast_args)


def process_command_args(cmd: ResolvedCommand) -> BoundArguments:
    args, kwargs = extract_kwargs_from_args(cmd.args, cmd.fn_sig, cmd.kwarg_map)

    processed_args = run_positional_preprocessors(args, cmd)

    assert_positional_arg_count_within_bounds(cmd.fn_sig, processed_args)

    cast_args = coerce_bound_args(cmd.fn_sig.bind(*processed_args, **kwargs))

    return cast_args
