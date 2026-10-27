from pathlib import Path

from instance import Instance


def json_serializer_helper(obj: object) -> object:
    match obj:
        case Path():
            return str(obj)
        case Instance():
            return obj.to_json()
        case _:
            raise TypeError(
                f"Object of type {type(obj).__name__} is not JSON serializable"
            )


def settings_json_postprocessor(config: dict):
        return {instance: Instance.from_json(data) for instance, data in config.items()}