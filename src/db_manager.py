import logging
from types import TracebackType
from typing import Any, Dict, List, Optional, Type

import psycopg2

from src.config import Config

logger = logging.getLogger(__name__)


class DBManager:
    """Класс для работы с данными в БД."""

    def __init__(self, config: Config) -> None:
        self.config: Config = config
        self.conn_string: str = config.get_db_connection_string()

    def __enter__(self) -> "DBManager":
        self.conn = psycopg2.connect(self.conn_string)
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if hasattr(self, "conn"):
            self.conn.close()

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """Получить компании и количество вакансий."""
        with psycopg2.connect(self.conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT e.name, COUNT(v.id) as vacancies_count
                    FROM employers e
                    LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                    GROUP BY e.name
                    ORDER BY vacancies_count DESC
                """
                )
                rows = cur.fetchall()
                return [
                    {
                        "name": row[0],
                        "vacancies_count": row[1],
                    }
                    for row in rows
                ]

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """Получить все вакансии."""
        with psycopg2.connect(self.conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT e.name as company_name, v.name, v.salary_from, v.salary_to, v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    ORDER BY v.salary_from DESC NULLS LAST
                """
                )
                rows = cur.fetchall()
                return [
                    {
                        "company_name": row[0],
                        "name": row[1],
                        "salary_from": row[2],
                        "salary_to": row[3],
                        "url": row[4],
                    }
                    for row in rows
                ]

    def get_avg_salary(self) -> Optional[float]:
        """Получить среднюю зарплату."""
        with psycopg2.connect(self.conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT AVG(COALESCE(salary_from, salary_to)) as avg_salary
                    FROM vacancies
                    WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                """
                )
                row = cur.fetchone()
                if row is None or row[0] is None:
                    return None
                return float(row[0])

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """Вакансии с зарплатой выше средней."""
        avg_salary = self.get_avg_salary()
        if avg_salary is None:
            return []

        with psycopg2.connect(self.conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT e.name as company_name, v.name, v.salary_from
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    WHERE (v.salary_from > %s OR v.salary_to > %s)
                    AND (v.salary_from IS NOT NULL OR v.salary_to IS NOT NULL)
                """,
                    (avg_salary, avg_salary),
                )
                rows = cur.fetchall()
                return [
                    {
                        "company_name": row[0],
                        "name": row[1],
                        "salary_from": row[2],
                    }
                    for row in rows
                ]

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Вакансии по ключевому слову."""
        with psycopg2.connect(self.conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT e.name as company_name, v.name
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    WHERE LOWER(v.name) LIKE LOWER(%s)
                """,
                    (f"%{keyword}%",),
                )
                rows = cur.fetchall()
                return [
                    {
                        "company_name": row[0],
                        "name": row[1],
                    }
                    for row in rows
                ]
