from .. import namespace, command

class CommandClass:

    
    @staticmethod
    @command()
    def CommandA():
        return "CommandA"