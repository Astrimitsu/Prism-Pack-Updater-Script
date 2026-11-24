from .ct import command


class SystemCommands:

    @staticmethod
    @command(("quit",), "Exit the program")
    def quit():
        raise SystemExit(0)