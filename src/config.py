import os
from typing import Dict


class Config:
    """Конфигурация приложения."""

    def __init__(self) -> None:
        self.db_params: Dict[str, str] = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
            "database": os.getenv("DB_NAME", "hh_vacancies"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", ""),
        }

    def get_db_connection_string(self) -> str:
        """Строка подключения к БД."""
        return (
            f"host={self.db_params['host']} "
            f"port={self.db_params['port']} "
            f"dbname={self.db_params['database']} "
            f"user={self.db_params['user']} "
            f"password={self.db_params['password']}"
        )
