import json


class Settings:
    def __init__(self, config = None, instance = None) -> None:
        self.config = config if config else {}
        self.instance = instance if instance else ""

    def from_disk(self) -> None:
        try:
            with open("settings.json") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            return

    def write_to_json(self) -> None:
        with open("settings.json", "w") as f:
            f.write(json.dumps(self.config, indent=4))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Settings):
            return NotImplemented
        return vars(self) == vars(other)
        


class InvalidInput(Exception):
    # Raised when command matches no valid commands
    pass
