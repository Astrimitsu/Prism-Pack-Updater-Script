from classes import Settings
import readline  # noqa: F401
from config import config


def main() -> None:

    settings = Settings()
    config(settings)


main()
