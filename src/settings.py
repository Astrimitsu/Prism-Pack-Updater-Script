import json
from pathlib import Path

import error_strings
from helpers import assert_glob_single_match
from instance import Instance
from json_helpers import json_serializer_helper, settings_json_postprocessor


class Settings:
    def __init__(self, config: dict | None = None, instance: str | None = None) -> None:
        self._config: dict[str, Instance] = config if config else {}
        self.instance: str | None = instance
        self.dirty: bool = False

    @staticmethod
    def from_disk(path: Path) -> Settings:
        try:
            with open(path) as f:
                config = json.load(f)
            settings_json_postprocessor(config)
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
        if self.instance:
            return Path(self._config[self.instance].path) / "minecraft" / Path(path)
        raise AttributeError(error_strings.ERR_INSTANCE_NOT_SET_WHEN_GETTING_PATH)

    def set_instance(self, alias: str) -> None:
        if not self.instance_exists(alias):
            raise ValueError(error_strings.ERR_INSTANCE_NONEXISTENT.format(alias))
        self.instance = alias

    def add_instance(self, raw_path: str, alias: str | None = None) -> None:
        path = Path(raw_path)
        if not alias:
            alias = path.stem
        if self.instance_exists(alias):
            raise ValueError(error_strings.ERR_INSTANCE_EXISTS.format(alias))
        if (path / "mmc-pack.json").exists():
            raise ValueError(
                error_strings.ERR_PATH_NOT_PRISM_INSTANCE.format(str(path))
            )

        assert_glob_single_match(path)

        self._config[alias] = Instance(path)
        self.dirty = True

    def remove_instance(self, alias: str) -> None:
        if not self.instance_exists(alias):
            raise ValueError(error_strings.ERR_INSTANCE_NONEXISTENT.format(alias))

        del self._config[alias]

        if self.instance == alias:
            self.instance = None

        self.dirty = True

    def add_file(self, file: str):
        pass

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Settings):
            return NotImplemented
        return vars(self) == vars(other)
