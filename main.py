import logging

from dotenv import load_dotenv

from src.api import HHApi
from src.config import Config
from src.database import Database
from src.db_manager import DBManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def main() -> None:
    load_dotenv()
    config = Config()
    logger.info("Приложение запущено")

    db = Database(config)
    db.create_database()
    db.create_tables()

    api = HHApi()
    companies = api.get_companies_info()
    vacancies = api.get_vacancies(companies)

    db.load_companies(companies)
    db.load_vacancies(vacancies)

    logger.info("Данные успешно загружены")

    db_manager = DBManager(config)
    show_menu(db_manager)


def show_menu(db_manager: DBManager) -> None:
    """Интерфейс взаимодействия с пользователем."""
    while True:
        print("\n" + "=" * 50)
        print("МЕНЮ:")
        print("1. Количество вакансий по компаниям")
        print("2. Все вакансии")
        print("3. Средняя зарплата")
        print("4. Вакансии выше средней зарплаты")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("Выберите пункт меню: ").strip()

        if choice == "1":
            companies_data = db_manager.get_companies_and_vacancies_count()
            print("\nКомпании и количество вакансий:")
            for company in companies_data:
                print(f"{company['name']} - {company['vacancies_count']} вакансий")

        elif choice == "2":
            vacancies_data = db_manager.get_all_vacancies()
            print(f"\nВсего вакансий: {len(vacancies_data)}")
            for vac in vacancies_data:
                salary_from = vac["salary_from"]
                salary_to = vac["salary_to"]

                if salary_from is None and salary_to is None:
                    salary = "Не указана"
                elif salary_from is not None and salary_to is not None:
                    salary = f"{salary_from:,} - {salary_to:,}"
                elif salary_from is not None:
                    salary = f"от {salary_from:,}"
                else:
                    salary = f"до {salary_to:,}"

                print(f"{vac['company_name']} | {vac['name']} | {salary}₽ | {vac['url']}")

        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            if avg_salary is None:
                print("\nЗарплата не указана ни в одной вакансии")
            else:
                print(f"\nСредняя зарплата по всем вакансиям: {avg_salary:,.0f}₽")

        elif choice == "4":
            high_salary_vacancies = db_manager.get_vacancies_with_higher_salary()
            print(f"\nВакансии выше средней зарплаты ({len(high_salary_vacancies)}):")
            for vac in high_salary_vacancies[:20]:
                salary_from = vac["salary_from"]
                if salary_from is None:
                    salary_str = "Зарплата не указана"
                else:
                    salary_str = f"{salary_from:,}₽+"
                print(f"{vac['company_name']} | {vac['name']} | {salary_str}")
        elif choice == "5":
            keyword = input("Введите ключевое слово: ").strip()
            keyword_vacancies = db_manager.get_vacancies_with_keyword(keyword)
            print(f"\nВакансии с '{keyword}' ({len(keyword_vacancies)}):")
            for vac in keyword_vacancies:
                print(f"{vac['company_name']} | {vac['name']}")
        elif choice == "0":
            logger.info("Приложение завершено")
            break
        else:
            print("Неверный выбор!")


if __name__ == "__main__":
    main()
