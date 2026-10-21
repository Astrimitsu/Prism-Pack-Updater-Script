import json
from pathlib import Path

from helpers import assert_glob_single_match, json_serializer_helper


class Settings:
    def __init__(self, config: dict | None = None, instance: str | None = None) -> None:
        self._config = config if config else {}
        self.instance = instance if instance else ""
        self.dirty = False

    @staticmethod
    def from_disk() -> Settings:
        try:
            with open("settings.json") as f:
                config = json.load(f)
            return Settings(config)
        except FileNotFoundError:
            return Settings()

    def get_instances(self):
        return [instance for instance in self._config]

    def instance_exists(self, alias: str) -> bool:
        return alias in self._config

    def write_to_json(self) -> None:
        if not self.dirty:
            return

        with open("settings.json", "w") as f:
            f.write(json.dumps(self._config, indent=4, default=json_serializer_helper))

    def path_to_instance_folder(self, path: Path) -> Path:
        return Path(self._config[self.instance]["path"]) / "minecraft" / Path(path)

    def set_instance(self, alias):
        if not self.instance_exists(alias):
            raise ValueError(f"Instance {alias} does not exist.")
        self.instance = alias

    def add_instance(self, raw_path: str, alias: str | None = None) -> None:
        path = Path(raw_path)
        if not alias:
            alias = path.stem
        if not self.instance_exists(alias):
            raise ValueError(f"Instance at {alias} already exists")
        if not (path / "mmc-pack.json").exists():
            raise ValueError(f"Directory at {path!s} is not a valid Prism instance")

        assert_glob_single_match(path)

        self._config[alias] = {"path": path, "additions": [], "removals": []}
        self.dirty = True

    def remove_instance(self, alias: str) -> None:
        if not self.instance_exists(alias):
            raise ValueError(f"Instance {alias} does not exist.")

        del self._config[alias]

        if self.instance == alias:
            self.instance = ""

        self.dirty = True

    def add_file(self, file: str):
        pass


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Settings):
            return NotImplemented
        return vars(self) == vars(other)