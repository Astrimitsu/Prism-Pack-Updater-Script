from commandtrie import command
import sys
from classes import CommandSignal

class SystemCommands:

    @staticmethod
    @command(("quit",), "Exit the program")
    def quit():
        sys.exit(0)

    @staticmethod
    @command(("done",), "Finish editing settings")
    def done():
        return CommandSignal.QUIT