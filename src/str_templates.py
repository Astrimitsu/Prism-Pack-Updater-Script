from typing import Final

ERR_NOT_DIRECTORY: Final[str] = "Item at {} is not a directory"
ERR_FILE_NOT_EXIST: Final[str] = "File at {} does not exist"
ERR_GLOB_TOO_MANY_MATCHES: Final[str] = "Input glob {} resolves to more than one file"
ERR_INSTANCE_NOT_SET_WHEN_GETTING_PATH: Final[str] = "Cannot resolve instance path: no active instance is set."
ERR_INSTANCE_NONEXISTENT: Final[str] = "Instance {} does not exist"
ERR_INSTANCE_EXISTS: Final[str] = "Instance at {} already exists"
ERR_PATH_NOT_PRISM_INSTANCE: Final[str] = "Directory at {} is not a valid Prism instance"