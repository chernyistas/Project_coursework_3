import logging
from dataclasses import dataclass
from typing import List, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class Company:
    id: int
    name: str
    url: str


@dataclass
class Vacancy:
    id: str
    name: str
    employer_id: int
    salary_from: Optional[int]
    salary_to: Optional[int]
    url: str


class HHApi:
    """Работа с API HH.ru."""

    BASE_URL = "https://api.hh.ru"
    HEADERS = {"User-Agent": "HhVacanciesParser/1.0"}

    # Популярные компании (employer_id из hh.ru)
    POPULAR_COMPANIES = [
        1740,  # Яндекс
        3529,  # 2ГИС (пример)
        15478,  # VK
        39305,  # Газпром нефть
        5817234,  # Газпром ID
        9498120,  # Яндекс Команда для бизнеса
        12465811,  # ИНТЕЛЛ
        1824833,  # ID:HR
        19,  # КВАРТА ВК
    ]

    def get_companies_info(self) -> List[Company]:
        """Получить информацию о компаниях."""
        companies = []
        for employer_id in self.POPULAR_COMPANIES[:10]:  # Берем первые 10
            try:
                url = f"{self.BASE_URL}/employers/{employer_id}"
                response = requests.get(url, headers=self.HEADERS)
                response.raise_for_status()

                data = response.json()
                companies.append(Company(id=data["id"], name=data["name"], url=data["alternate_url"]))
                logger.info(f"Получена информация о компании: {data['name']}")

            except requests.RequestException as e:
                logger.error(f"Ошибка при получении компании {employer_id}: {e}")
                continue

        return companies

    def get_vacancies(self, companies: List[Company]) -> List[Vacancy]:
        """Получить вакансии компаний."""
        all_vacancies = []

        for company in companies:
            page = 0
            pages = 1

            while page < pages:
                try:
                    url = f"{self.BASE_URL}/vacancies"
                    params = {"employer_id": company.id, "page": page, "per_page": 100}

                    response = requests.get(url, headers=self.HEADERS, params=params)
                    response.raise_for_status()

                    data = response.json()
                    pages = data.get("pages", 1)

                    for item in data.get("items", []):
                        salary = item.get("salary")

                        if salary:
                            salary_from = salary.get("from")
                            salary_to = salary.get("to")
                        else:
                            salary_from = None
                            salary_to = None

                        vacancy = Vacancy(
                            id=item["id"],
                            name=item["name"],
                            employer_id=company.id,
                            salary_from=salary_from,
                            salary_to=salary_to,
                            url=item.get("alternate_url"),
                        )
                        all_vacancies.append(vacancy)

                    logger.info(f"Компания {company.name}: страница {page + 1}/{pages}")
                    page += 1

                except requests.RequestException as e:
                    logger.error(f"Ошибка при получении вакансий компании {company.name}: {e}")
                    break

        logger.info(f"Всего получено вакансий: {len(all_vacancies)}")
        return all_vacancies
