from collections.abc import Iterator
from inspect import Signature

import error_strings
from classes import InvalidCommandArgCount, KwargNotFound
from consts import ANY_KWARGS
from sig_tools import get_function_kwargs


def extract_kwargs_from_args(
    input_args: list[str], sig: Signature, kwarg_map: dict[str, str]
) -> tuple[list[str], dict[str, str | bool]]:
    fn_kwargs: dict[object, object] = get_function_kwargs(sig)
    kwargs: dict[str, str | bool] = {}
    args: list = []

    kwarg_iterator = iter(input_args)
    for token in kwarg_iterator:
        if not is_kwarg(token):
            args.append(token)
            continue

        resolved_token: str = resolve_param_name(token, kwarg_map)

        validate_param_exists(resolved_token, fn_kwargs)

        kwarg_default: object = get_kwarg_param_default(resolved_token, fn_kwargs)

        if isinstance(kwarg_default, bool):
            kwargs[resolved_token] = not kwarg_default
            continue

        kwargs[resolved_token] = get_and_consume_next_token(kwarg_iterator, token)

    return args, kwargs


def is_kwarg(token: str) -> bool:
    return token.startswith("-") and not token.startswith("---")


def resolve_param_name(token: str, kwarg_map: dict[str, str]) -> str:
    cleaned_token = token.lstrip("-").replace("-", "_")
    return kwarg_map.get(cleaned_token, cleaned_token)


def validate_param_exists(token: str, fn_kwargs: dict[object, object]) -> None:
    if ANY_KWARGS not in fn_kwargs and token not in fn_kwargs:
        raise KwargNotFound(error_strings.ERR_KWARG_NOT_FOUND.format(token))


def get_kwarg_param_default(token: str, fn_kwargs: dict[object, object]) -> object:
    return fn_kwargs.get(token, fn_kwargs[ANY_KWARGS])


def get_and_consume_next_token(iterator: Iterator, raw_token: str) -> str:
    try:
        kwarg_value = next(iterator)
        if is_kwarg(kwarg_value):
            raise ValueError
    except (StopIteration, ValueError):
        raise InvalidCommandArgCount(
            error_strings.ERR_MISSING_KWARG_ARGUMENT.format(raw_token)
        )
    return kwarg_value
