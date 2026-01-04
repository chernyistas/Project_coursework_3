from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from src.db_manager import DBManager

load_dotenv()


def test_get_companies_and_vacancies_count(db_manager: DBManager) -> None:
    """
    Тест проверяет, что метод возвращает список словарей
    и не выбрасывает исключений.
    """
    result: List[Dict[str, Any]] = db_manager.get_companies_and_vacancies_count()
    assert isinstance(result, list)
    if result:
        assert "name" in result[0]
        assert "vacancies_count" in result[0]


def test_get_all_vacancies(db_manager: DBManager) -> None:
    """
    Тест проверяет, что метод возвращает список вакансий
    и в элементах есть ожидаемые ключи.
    """
    result: List[Dict[str, Any]] = db_manager.get_all_vacancies()
    assert isinstance(result, list)
    if result:
        v = result[0]
        assert "company_name" in v
        assert "name" in v
        assert "url" in v


def test_get_avg_salary(db_manager: DBManager) -> None:
    """
    Тест проверяет, что средняя зарплата либо не посчитана (None),
    либо представлена числом.
    """
    result: Optional[float] = db_manager.get_avg_salary()
    assert result is None or isinstance(result, (float, int))


def test_get_vacancies_with_higher_salary(db_manager: DBManager) -> None:
    """
    Тест проверяет, что метод возвращает список.
    """
    result: List[Dict[str, Any]] = db_manager.get_vacancies_with_higher_salary()
    assert isinstance(result, list)


def test_get_vacancies_with_keyword(db_manager: DBManager) -> None:
    """
    Тест проверяет, что поиск по ключевому слову
    возвращает список словарей.
    """
    result: List[Dict[str, Any]] = db_manager.get_vacancies_with_keyword("python")
    assert isinstance(result, list)
    if result:
        assert "company_name" in result[0]
        assert "name" in result[0]
