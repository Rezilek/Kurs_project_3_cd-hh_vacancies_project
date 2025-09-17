from api import HHAPI, get_employer_data, get_vacancies_data
from database import DatabaseManager
from db_manager import DBManager
from models import Employer, Vacancy
from config import create_config_template, get_db_config
import os
from typing import List, Dict, Any


def check_config() -> bool:
    """Проверка наличия и корректности конфигурационного файла"""
    config_file = 'config/database.ini'

    if not os.path.exists(config_file):
        print("Конфигурационный файл не найден!")
        create_config_template()
        return False

    try:
        config = get_db_config()
        # Проверяем, не используются ли значения по умолчанию
        if config['user'] == 'your_username' or config['password'] == 'your_password':
            print("Пожалуйста, настройте config/database.ini с вашими данными PostgreSQL")
            return False
        return True
    except Exception as e:
        print(f"Ошибка в конфигурационном файле: {e}")
        return False


def setup_database() -> DatabaseManager:
    """Настройка и создание базы данных"""
    db_manager = DatabaseManager()

    try:
        # Создание базы данных
        db_manager.create_database('hh_vacancies')

        # Обновляем конфиг для подключения к созданной БД
        db_manager.config['database'] = 'hh_vacancies'
        db_manager.connect()

        # Создание таблиц
        db_manager.create_tables()

        return db_manager

    except Exception as e:
        print(f"Ошибка при настройке базы данных: {e}")
        return None


def main():
    """Основная функция программы"""

    # Проверка конфигурации
    if not check_config():
        return

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

    # Настройка базы данных
    print("Настройка базы данных...")
    db_manager = setup_database()
    if not db_manager:
        return

    # Инициализация API
    api = HHAPI()

    print("Получение данных с hh.ru...")

    try:
        # Получение данных о работодателях
        employers_data = get_employer_data(api, employer_ids)

        # Получение данных о вакансиях
        vacancies_data = get_vacancies_data(api, employer_ids)

        # Преобразование данных в модели
        employers = []
        vacancies = []

        for emp_id, emp_data in employers_data.items():
            employers.append(Employer.from_json(emp_data))

        for emp_id, vac_list in vacancies_data.items():
            for vac_data in vac_list:
                vacancies.append(Vacancy.from_json(vac_data))

        print(f"Получено {len(employers)} работодателей и {len(vacancies)} вакансий")

        # Загрузка данных
        db_manager.load_data(employers, vacancies)

    except Exception as e:
        print(f"Ошибка при получении или загрузке данных: {e}")
    finally:
        # Закрытие соединения
        db_manager.disconnect()

    # Работа с данными через DBManager
    db_manager = DBManager()

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
            companies = db_manager.get_companies_and_vacancies_count()
            for company in companies:
                print(f"{company['company']}: {company['vacancies_count']} вакансий")

        elif choice == '2':
            print("\nСПИСОК ВСЕХ ВАКАНСИЙ:")
            print("-" * 80)
            all_vacancies = db_manager.get_all_vacancies()
            for vac in all_vacancies:
                print(f"Компания: {vac['company']}")
                print(f"Вакансия: {vac['vacancy']}")
                print(f"Зарплата: {vac['salary'] or 'Не указана'}")
                print(f"Ссылка: {vac['url']}")
                print("-" * 40)

        elif choice == '3':
            avg_salary = db_manager.get_avg_salary()
            print(f"\nСРЕДНЯЯ ЗАРПЛАТА ПО ВАКАНСИЯМ: {avg_salary} руб.")

        elif choice == '4':
            print("\nВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ:")
            print("-" * 80)
            high_salary_vacancies = db_manager.get_vacancies_with_higher_salary()
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
                found_vacancies = db_manager.get_vacancies_with_keyword(keyword)
                for vac in found_vacancies:
                    print(f"Компания: {vac['company']}")
                    print(f"Вакансия: {vac['vacancy']}")
                    print(f"Зарплата: {vac['salary'] or 'Не указана'}")
                    print(f"Ссылка: {vac['url']}")
                    print("-" * 40)
            else:
                print("Ключевое слово не может быть пустым!")

        elif choice == '0':
            print("Выход из программы...")
            break

        else:
            print("Неверный выбор! Попробуйте еще раз.")


if __name__ == "__main__":
    main()
