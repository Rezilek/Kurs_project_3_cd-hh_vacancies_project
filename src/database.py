import configparser
from typing import Dict, List, Optional

import psycopg2
from psycopg2 import sql

from src.models import Employer, Vacancy


def _read_config(config_file: str) -> Dict[str, str]:
    """Чтение конфигурации из файла"""
    config = configparser.ConfigParser()
    config.read(config_file)
    return {
        "host": config["postgresql"]["host"],
        "database": config["postgresql"]["database"],
        "user": config["postgresql"]["user"],
        "password": config["postgresql"]["password"],
        "port": config["postgresql"]["port"],
    }


class DatabaseManager:
    """Класс для управления базой данных PostgreSQL"""

    def __init__(self, config_file: str = 'config/database.ini') -> None:
        """
        Инициализация менеджера базы данных

        Args:
            config_file: путь к файлу конфигурации
        """
        self.config_file = config_file
        self.config = self._read_config(config_file)
        self.connection: Optional[psycopg2.extensions.connection] = None

    def _read_config(self, config_file: str) -> Dict[str, str]:
        """Чтение конфигурации из файла"""
        config = configparser.ConfigParser()
        config.read(config_file)
        return {
            "host": config["postgresql"]["host"],
            "database": config["postgresql"]["database"],
            "user": config["postgresql"]["user"],
            "password": config["postgresql"]["password"],
            "port": config["postgresql"]["port"],
        }

    def _get_connection_string(self, db_name: Optional[str] = None) -> str:
        """Преобразование конфигурации в строку подключения"""
        database = db_name or self.config['database']
        return (
            f"host={self.config['host']} "
            f"dbname={database} "
            f"user={self.config['user']} "
            f"password={self.config['password']} "
            f"port={self.config['port']}"
        )

    def connect(self, db_name: Optional[str] = None) -> None:
        """Подключение к базе данных"""
        try:
            database = db_name or self.config['database']
            connection_string = (
                f"host={self.config['host']} "
                f"dbname={database} "
                f"user={self.config['user']} "
                f"password={self.config['password']} "
                f"port={self.config['port']}"
            )
            self.connection = psycopg2.connect(connection_string)
            print("Успешное подключение к базе данных")
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise

    def disconnect(self) -> None:
        """Отключение от базы данных"""
        if self.connection:
            self.connection.close()
            print("Отключение от базы данных")
            self.connection = None

    def create_database(self, db_name: str) -> None:
        """
        Создание базы данных

        Args:
            db_name: название базы данных
        """
        # Временное подключение к postgres для создания БД
        temp_config = self.config.copy()
        temp_config["database"] = "postgres"

        try:
            # Создаем строку подключения
            connection_string = (
                f"host={temp_config['host']} "
                f"dbname={temp_config['database']} "
                f"user={temp_config['user']} "
                f"password={temp_config['password']} "
                f"port={temp_config['port']}"
            )

            conn = psycopg2.connect(connection_string)
            conn.autocommit = True
            cursor = conn.cursor()

            # Проверяем, существует ли база данных
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name))
                )
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
            if self.connection:
                with self.connection.cursor() as cursor:
                    # Таблица employers
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS employers (
                            id INTEGER PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            url TEXT,
                            alternate_url TEXT,
                            description TEXT
                        )
                    """
                    )

                    # Таблица vacancies
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS vacancies (
                            id INTEGER PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            url TEXT,
                            alternate_url TEXT,
                            employer_id INTEGER REFERENCES employers(id) ON DELETE CASCADE,
                            salary_from INTEGER,
                            salary_to INTEGER,
                            currency VARCHAR(10),
                            salary_gross BOOLEAN,
                            description TEXT,
                            experience VARCHAR(100),
                            employment VARCHAR(100)
                        )
                    """
                    )

                    self.connection.commit()
                    print("Таблицы созданы успешно")
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            print(f"Ошибка при создании таблиц: {e}")
            raise

    def insert_employer(self, employer: Employer) -> None:
        """
        Вставка данных работодателя

        Args:
            employer: объект Employer
        """
        if not self.connection:
            self.connect()

        try:
            if self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO employers (id, name, url, alternate_url, description)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        url = EXCLUDED.url,
                        alternate_url = EXCLUDED.alternate_url,
                        description = EXCLUDED.description
                    """,
                        (
                            employer.id,
                            employer.name,
                            employer.url,
                            employer.alternate_url,
                            employer.description,
                        ),
                    )
                    self.connection.commit()
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            print(f"Ошибка при вставке работодателя {employer.id}: {e}")

    def insert_vacancy(self, vacancy: Vacancy) -> None:
        """
        Вставка данных вакансии

        Args:
            vacancy: объект Vacancy
        """
        if not self.connection:
            self.connect()

        salary_from = vacancy.salary.from_ if vacancy.salary else None
        salary_to = vacancy.salary.to if vacancy.salary else None
        currency = vacancy.salary.currency if vacancy.salary else None
        salary_gross = vacancy.salary.gross if vacancy.salary else None

        try:
            if self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO vacancies (
                            id, name, url, alternate_url, employer_id,
                            salary_from, salary_to, currency, salary_gross,
                            description, experience, employment
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        url = EXCLUDED.url,
                        alternate_url = EXCLUDED.alternate_url,
                        employer_id = EXCLUDED.employer_id,
                        salary_from = EXCLUDED.salary_from,
                        salary_to = EXCLUDED.salary_to,
                        currency = EXCLUDED.currency,
                        salary_gross = EXCLUDED.salary_gross,
                        description = EXCLUDED.description,
                        experience = EXCLUDED.experience,
                        employment = EXCLUDED.employment
                    """,
                        (
                            vacancy.id,
                            vacancy.name,
                            vacancy.url,
                            vacancy.alternate_url,
                            vacancy.employer_id,
                            salary_from,
                            salary_to,
                            currency,
                            salary_gross,
                            vacancy.description,
                            vacancy.experience,
                            vacancy.employment,
                        ),
                    )
                    self.connection.commit()
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            print(f"Ошибка при вставке вакансии {vacancy.id}: {e}")

    def load_data(self, employers: List[Employer], vacancies: List[Vacancy]) -> None:
        """
        Загрузка данных в базу данных

        Args:
            employers: список работодателей
            vacancies: список вакансий
        """
        print("Начало загрузки данных в базу данных...")

        # Загрузка работодателей
        for employer in employers:
            self.insert_employer(employer)

        # Загрузка вакансий
        for vacancy in vacancies:
            self.insert_vacancy(vacancy)

        print("Данные успешно загружены в базу данных")
