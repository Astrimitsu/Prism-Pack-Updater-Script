from collections.abc import Iterator, Mapping, Sequence
from inspect import Signature

import error_strings
from consts import ANY_KWARGS
from exception_classes import InvalidCommandArgCount, KwargNotFound

from f_cli.sig_utils import get_function_kwargs


def extract_kwargs_from_args(
    input_args: Sequence[str], sig: Signature, kwarg_map: Mapping[str, str]
) -> tuple[list[str], dict[str, str | bool]]:
    fn_kwargs: dict[object, object] = get_function_kwargs(sig)
    kwargs: dict[str, str | bool] = {}
    args: list[str] = []

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

        kwargs[resolved_token] = consume_kwarg_value(kwarg_iterator, token)

    return args, kwargs


def is_kwarg(token: str) -> bool:
    return token.startswith("-") and not token.startswith("---")


def resolve_param_name(token: str, kwarg_map: Mapping[str, str]) -> str:
    cleaned_token = token.lstrip("-").replace("-", "_")
    return kwarg_map.get(cleaned_token, cleaned_token)


def validate_param_exists(token: str, fn_kwargs: Mapping[object, object]) -> None:
    if ANY_KWARGS not in fn_kwargs and token not in fn_kwargs:
        raise KwargNotFound(error_strings.ERR_KWARG_NOT_FOUND.format(token))


def get_kwarg_param_default(token: str, fn_kwargs: Mapping[object, object]) -> object:
    return fn_kwargs.get(token, fn_kwargs[ANY_KWARGS])


def consume_kwarg_value(iterator: Iterator, raw_token: str) -> str:
    try:
        kwarg_value = next(iterator)
        if is_kwarg(kwarg_value):
            raise ValueError
        
    except (StopIteration, ValueError):
        raise InvalidCommandArgCount(
            error_strings.ERR_MISSING_KWARG_ARGUMENT.format(raw_token)
        )
    return kwarg_value
