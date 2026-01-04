import pytest

from src.config import Config
from src.db_manager import DBManager


@pytest.fixture
def db_manager() -> DBManager:
    """Фикстура, возвращающая экземпляр DBManager."""
    config: Config = Config()
    return DBManager(config)
