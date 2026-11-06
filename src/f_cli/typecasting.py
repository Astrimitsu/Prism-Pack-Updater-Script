from inspect import BoundArguments, Parameter
from types import UnionType
from typing import get_args


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
