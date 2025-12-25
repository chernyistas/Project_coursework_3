from decimal import Decimal
from typing import Any, Dict, List, Optional

import pytest
from dotenv import load_dotenv

from src.config import Config
from src.db_manager import DBManager


@pytest.fixture
def db_manager() -> DBManager:
    """Фикстура, возвращающая экземпляр DBManager."""
    config: Config = Config()
    return DBManager(config)


load_dotenv()


def test_get_companies_and_vacancies_count(db_manager: DBManager) -> None:
    """Тест метода получения компаний и количества вакансий."""
    result: List[Dict[str, Any]] = db_manager.get_companies_and_vacancies_count()
    assert isinstance(result, list)


load_dotenv()


def test_get_avg_salary(db_manager: DBManager) -> None:
    """Тест метода средней зарплаты."""
    result: Optional[float | Decimal] = db_manager.get_avg_salary()
    assert result is None or isinstance(result, (float, Decimal))
