import json


class Settings:
    mod_dir = "minecraft/mods"
    def __init__(self) -> None:
        try:
            with open("settings.json") as f:
                self.config = json.loads(f.read())
        except FileNotFoundError:
            self.config = {}
        self.instance = ""

    def write_to_json(self) -> None:
        with open("settings.json", "w") as f:
            f.write(json.dumps(self.config, indent=4))


class InvalidInput(BaseException):
    # Raised when command matches no valid commands
    pass
