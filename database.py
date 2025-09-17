import psycopg2
from psycopg2 import sql
from typing import Dict, List, Any
from models import Employer, Vacancy
from config import get_db_config


class DatabaseManager:
    """Класс для управления базой данных PostgreSQL"""

    def __init__(self, config_file: str = 'config/database.ini'):
        self.config = get_db_config(config_file)
        self.connection = None

    def connect(self) -> None:
        """Подключение к базе данных"""
        try:
            self.connection = psycopg2.connect(**self.config)
            print("Успешное подключение к базе данных")
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise

    def disconnect(self) -> None:
        """Отключение от базы данных"""
        if self.connection:
            self.connection.close()

    def create_database(self, db_name: str) -> None:
        """Создание базы данных"""
        temp_config = self.config.copy()
        temp_config['database'] = 'postgres'

        try:
            conn = psycopg2.connect(**temp_config)
            conn.autocommit = True
            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
                print(f"База данных {db_name} создана успешно")
            else:
                print(f"База данных {db_name} уже существует")

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка при создании базы данных: {e}")
            raise

    def create_tables(self) -> None:
        """Создание таблиц в базе данных"""
        if not self.connection:
            self.connect()

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS employers (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        url TEXT,
                        alternate_url TEXT,
                        description TEXT
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vacancies (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        url TEXT,
                        alternate_url TEXT,
                        employer_id INTEGER REFERENCES employers(id),
                        salary_from INTEGER,
                        salary_to INTEGER,
                        currency VARCHAR(10),
                        description TEXT
                    )
                """)

                self.connection.commit()
                print("Таблицы созданы успешно")

        except Exception as e:
            self.connection.rollback()
            print(f"Ошибка при создании таблиц: {e}")
            raise

    def insert_employer(self, employer: Employer) -> None:
        """Вставка данных работодателя"""
        if not self.connection:
            self.connect()

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO employers (id, name, url, alternate_url, description)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    url = EXCLUDED.url,
                    alternate_url = EXCLUDED.alternate_url,
                    description = EXCLUDED.description
                """, (
                    employer.id,
                    employer.name,
                    employer.url,
                    employer.alternate_url,
                    employer.description
                ))
                self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(f"Ошибка при вставке работодателя {employer.id}: {e}")

    def insert_vacancy(self, vacancy: Vacancy) -> None:
        """Вставка данных вакансии"""
        if not self.connection:
            self.connect()

        salary_from = vacancy.salary.from_ if vacancy.salary else None
        salary_to = vacancy.salary.to if vacancy.salary else None
        currency = vacancy.salary.currency if vacancy.salary else None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO vacancies (id, name, url, alternate_url, employer_id,
                    salary_from, salary_to, currency, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    url = EXCLUDED.url,
                    alternate_url = EXCLUDED.alternate_url,
                    employer_id = EXCLUDED.employer_id,
                    salary_from = EXCLUDED.salary_from,
                    salary_to = EXCLUDED.salary_to,
                    currency = EXCLUDED.currency,
                    description = EXCLUDED.description
                """, (
                    vacancy.id,
                    vacancy.name,
                    vacancy.url,
                    vacancy.alternate_url,
                    vacancy.employer_id,
                    salary_from,
                    salary_to,
                    currency,
                    vacancy.description
                ))
                self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(f"Ошибка при вставке вакансии {vacancy.id}: {e}")

    def load_data(self, employers: List[Employer], vacancies: List[Vacancy]) -> None:
        """Загрузка данных в базу данных"""
        print("Начало загрузки данных в базу данных...")

        for employer in employers:
            self.insert_employer(employer)

        for vacancy in vacancies:
            self.insert_vacancy(vacancy)

        print("Данные успешно загружены в базу данных")
        