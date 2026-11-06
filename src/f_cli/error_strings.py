from typing import Final

ERR_COMMAND_NONEXISTENT: Final[str] = "Command at {} does not exist"
ERR_MISSING_KWARG_ARGUMENT: Final[str] = "Command {} is missing parameter"
ERR_KWARG_NOT_FOUND: Final[str] = "{} is not a valid flag or parameter"
ERR_INVALID_COMMAND_ARGCOUNT: Final[str] = "Invalid argument count"
ERR_OBJECT_ALREADY_REGISTERED: Final[str] = "Object of type {} is already registered"