class CommandNotExist(Exception):
    # Raised when command matches no valid commands
    pass

class InvalidCommandArgCount(Exception):
    pass