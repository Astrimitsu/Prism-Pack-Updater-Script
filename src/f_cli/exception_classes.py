from enum import StrEnum, auto


class CommandNotExist(Exception):
    # Raised when command matches no valid commands
    pass

class InvalidCommandArgCount(Exception):
    pass

class KwargNotFound(Exception):
    pass

class CommandSignal(StrEnum):
    SUCCESS = auto()
    QUIT = auto()