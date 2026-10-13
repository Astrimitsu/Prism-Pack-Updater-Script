import json


class Settings:
    def __init__(self) -> None:
        try:
            with open("settings.json") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}
        self.instance = ""

    def write_to_json(self) -> None:
        with open("settings.json", "w") as f:
            f.write(json.dumps(self.config, indent=4))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Settings):
            return NotImplemented
        return self.config == other.config and self.instance == other.instance
        


class InvalidInput(Exception):
    # Raised when command matches no valid commands
    pass
