import pytest

from pathlib import Path
from src.settings import Settings


class TestConfig:

    @pytest.fixture
    def settings_object(self):
        return Settings()