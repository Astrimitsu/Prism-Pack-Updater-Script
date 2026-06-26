from classes import InvalidInput


def min_max_inputs(args: list, min: int, max: int) -> None:
    if len(args) - 1 < min or len(args) - 1 > max:
        print("maxinput triggered")
        raise InvalidInput
