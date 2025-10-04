import sys
import os

# Добавляем путь к src для корректного импорта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api import HHAPI, get_employer_data, get_vacancies_data
from src.database import DatabaseManager
from src.db_manager import DBManager
from src.models import Employer, Vacancy
from typing import List


def main() -> None:
    """Основная функция программы"""

    # Список ID интересных компаний
    employer_ids = [
        1740,  # Яндекс
        15478,  # VK
        3529,  # Сбер
        907345,  # Тинькофф
        1057,  # Касперский
        78638,  # 1С
        2180,  # Ozon
        87021,  # Wildberries
        3776,  # МТС
        39305  # Газпром нефть
    ]

    # Инициализация API
    api = HHAPI()

    print("Получение данных с hh.ru...")

    # Получение данных о работодателях
    employers_data = get_employer_data(api, employer_ids)

    # Получение данных о вакансиях
    vacancies_data = get_vacancies_data(api, employer_ids)

    # Преобразование данных в модели
    employers: List[Employer] = []
    vacancies: List[Vacancy] = []

    for emp_id, emp_data in employers_data.items():
        employers.append(Employer.from_json(emp_data))

    for emp_id, vac_list in vacancies_data.items():
        for vac_data in vac_list:
            vacancies.append(Vacancy.from_json(vac_data))

    print(f"Получено {len(employers)} работодателей и {len(vacancies)} вакансий")

    # Инициализация менеджера базы данных
    db_manager = DatabaseManager()

    # Создание базы данных
    try:
        db_manager.create_database('hh_vacancies')
    except Exception as e:
        print(f"Ошибка при создании БД: {e}")

    # Подключение к созданной базе данных
    db_manager.config['database'] = 'hh_vacancies'
    try:
        db_manager.connect()
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return

    # Создание таблиц
    try:
        db_manager.create_tables()
    except Exception as e:
        print(f"Ошибка создания таблиц: {e}")
        return

    # Загрузка данных
    try:
        db_manager.load_data(employers, vacancies)
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return

    # Закрытие соединения
    db_manager.disconnect()

    # Работа с данными через DBManager
    db_manager_instance = DBManager()

    while True:
        print("\n" + "=" * 50)
        print("МЕНЮ УПРАВЛЕНИЯ БАЗОЙ ДАННЫХ ВАКАНСИЙ")
        print("=" * 50)
        print("1. Список компаний и количество вакансий")
        print("2. Список всех вакансий")
        print("3. Средняя зарплата по вакансиям")
        print("4. Вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")
        print("=" * 50)

        choice = input("Выберите действие: ").strip()

        if choice == '1':
            print("\nСПИСОК КОМПАНИЙ И КОЛИЧЕСТВО ВАКАНСИЙ:")
            print("-" * 50)
            companies = db_manager_instance.get_companies_and_vacancies_count()
            for company in companies:
                print(f"{company['company']}: {company['vacancies_count']} вакансий")

        elif choice == '2':
            print("\nСПИСОК ВСЕХ ВАКАНСИЙ:")
            print("-" * 80)
            all_vacancies = db_manager_instance.get_all_vacancies()
            for vac in all_vacancies:
                print(f"Компания: {vac['company']}")
                print(f"Вакансия: {vac['vacancy']}")
                print(f"Зарплата: {vac['salary'] or 'Не указана'}")
                print(f"Ссылка: {vac['url']}")
                print("-" * 40)

        elif choice == '3':
            avg_salary = db_manager_instance.get_avg_salary()
            print(f"\nСРЕДНЯЯ ЗАРПЛАТА ПО ВАКАНСИЯМ: {avg_salary} руб.")

        elif choice == '4':
            print("\nВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ:")
            print("-" * 80)
            high_salary_vacancies = db_manager_instance.get_vacancies_with_higher_salary()
            for vac in high_salary_vacancies:
                print(f"Компания: {vac['company']}")
                print(f"Вакансия: {vac['vacancy']}")
                print(f"Зарплата: {vac['salary']}")
                print(f"Ссылка: {vac['url']}")
                print("-" * 40)

        elif choice == '5':
            keyword = input("Введите ключевое слово для поиска: ").strip()
            if keyword:
                print(f"\nРЕЗУЛЬТАТЫ ПОИСКА ПО СЛОВУ '{keyword}':")
                print("-" * 80)
                found_vacancies = db_manager_instance.get_vacancies_with_keyword(keyword)
                if found_vacancies:
                    for vac in found_vacancies:
                        print(f"Компания: {vac['company']}")
                        print(f"Вакансия: {vac['vacancy']}")
                        print(f"Зарплата: {vac['salary'] or 'Не указана'}")
                        print(f"Ссылка: {vac['url']}")
                        print("-" * 40)
                else:
                    print("Вакансии не найдены")
            else:
                print("Ключевое слово не может быть пустым!")

        elif choice == '0':
            print("Выход из программы...")
            break

        else:
            print("Неверный выбор! Попробуйте еще раз.")


if __name__ == "__main__":
    main()