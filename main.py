from classes import Settings
from config import config
import platform
if platform.system() == "Linux":
    import readline  # noqa: F401


def main() -> None:

    settings = Settings()
    config(settings)

main()
