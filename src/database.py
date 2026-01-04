import logging
from typing import List

import psycopg2

from src.api import Company, Vacancy
from src.config import Config

logger = logging.getLogger(__name__)


class Database:
    """Работа с базой данных PostgreSQL."""

    def __init__(self, config: Config):
        self.config = config
        self.conn_string = config.get_db_connection_string()

    def create_database(self) -> None:
        """Создать базу данных."""
        try:
            temp_conn = psycopg2.connect(
                f"host={self.config.db_params['host']} "
                f"port={self.config.db_params['port']} "
                f"user={self.config.db_params['user']} "
                f"password={self.config.db_params['password']}"
            )
            temp_conn.autocommit = True
            cursor = temp_conn.cursor()

            cursor.execute(
                f"""
                SELECT 1 FROM pg_catalog.pg_database
                WHERE datname = '{self.config.db_params['database']}'
            """
            )

            if not cursor.fetchone():
                cursor.execute(f"CREATE DATABASE {self.config.db_params['database']}")
                logger.info(f"База данных '{self.config.db_params['database']}' создана")
            else:
                logger.info(f"База данных '{self.config.db_params['database']}' уже существует")

            cursor.close()
            temp_conn.close()

        except Exception as e:
            logger.error(f"Ошибка создания БД: {e}")

    def create_tables(self) -> None:
        """Создать таблицы."""
        with psycopg2.connect(self.conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS employers (
                        id SERIAL PRIMARY KEY,
                        employer_id INTEGER UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        url TEXT
                    )
                """
                )

                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS vacancies (
                        id SERIAL PRIMARY KEY,
                        vacancy_id VARCHAR(50) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        employer_id INTEGER REFERENCES employers(employer_id),
                        salary_from INTEGER,
                        salary_to INTEGER,
                        url TEXT
                    )
                """
                )

                conn.commit()
                logger.info("Таблицы созданы")

    def load_companies(self, companies: List[Company]) -> None:
        """Загрузить компании."""
        with psycopg2.connect(self.conn_string) as conn:
            with conn.cursor() as cur:
                for company in companies:
                    try:
                        cur.execute(
                            """
                            INSERT INTO employers (employer_id, name, url)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (employer_id) DO NOTHING
                        """,
                            (company.id, company.name, company.url),
                        )
                    except Exception as e:
                        logger.error(f"Ошибка загрузки компании {company.name}: {e}")

                conn.commit()
                logger.info(f"Загружено компаний: {len(companies)}")

    def load_vacancies(self, vacancies: List[Vacancy]) -> None:
        """Загрузить вакансии."""
        with psycopg2.connect(self.conn_string) as conn:
            with conn.cursor() as cur:
                for vacancy in vacancies:
                    try:
                        cur.execute(
                            """
                            INSERT INTO vacancies (vacancy_id, name, employer_id, salary_from, salary_to, url)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (vacancy_id) DO NOTHING
                        """,
                            (
                                vacancy.id,
                                vacancy.name,
                                vacancy.employer_id,
                                vacancy.salary_from,
                                vacancy.salary_to,
                                vacancy.url,
                            ),
                        )
                    except Exception as e:
                        logger.error(f"Ошибка загрузки вакансии {vacancy.name}: {e}")

                conn.commit()
                logger.info(f"Загружено вакансий: {len(vacancies)}")
