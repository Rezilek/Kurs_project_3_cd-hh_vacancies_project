import psycopg2  # type: ignore
from typing import List, Dict, Any, Optional
import configparser


class DBManager:
    """Класс для работы с данными в БД PostgreSQL"""

    def __init__(self, config_file: str = 'config/database.ini') -> None:
        """
        Инициализация менеджера базы данных

        Args:
            config_file: путь к файлу конфигурации
        """
        self.config = self._read_config(config_file)
        self.connection: Optional[psycopg2.extensions.connection] = None

    def _read_config(self, config_file: str) -> Dict[str, str]:
        """Чтение конфигурации из файла"""
        config = configparser.ConfigParser()
        config.read(config_file)
        return {
            'host': config['postgresql']['host'],
            'database': config['postgresql']['database'],
            'user': config['postgresql']['user'],
            'password': config['postgresql']['password'],
            'port': config['postgresql']['port']
        }

    def _get_connection_string(self) -> dict:
        """Возвращает параметры подключения в виде словаря"""
        return {
            'host': self.config['host'],
            'database': self.config['database'],
            'user': self.config['user'],
            'password': self.config['password'],
            'port': self.config['port']
        }

    def connect(self) -> None:
        """Подключение к базе данных"""
        try:
            # Используем отдельные параметры вместо строки подключения
            self.connection = psycopg2.connect(
                host=self.config['host'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                port=self.config['port']
            )
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise

    def disconnect(self) -> None:
        """Отключение от базы данных"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """
        Получить список всех компаний и количество вакансий у каждой компании

        Returns:
            List[Dict]: список словарей с данными компаний и количеством вакансий
        """
        self.connect()
        result: List[Dict[str, Any]] = []
        try:
            if self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT e.name, COUNT(v.id) as vacancy_count
                        FROM employers e
                        LEFT JOIN vacancies v ON e.id = v.employer_id
                        GROUP BY e.id, e.name
                        ORDER BY vacancy_count DESC
                    """)
                    for row in cursor.fetchall():
                        result.append({
                            'company': row[0],
                            'vacancies_count': row[1]
                        })
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
        finally:
            self.disconnect()
        return result

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получить список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию

        Returns:
            List[Dict]: список словарей с данными вакансий
        """
        self.connect()
        result: List[Dict[str, Any]] = []
        try:
            if self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT
                            e.name as company_name,
                            v.name as vacancy_name,
                            v.salary_from,
                            v.salary_to,
                            v.currency,
                            v.alternate_url
                        FROM vacancies v
                        JOIN employers e ON v.employer_id = e.id
                        ORDER BY e.name, v.name
                    """)
                    for row in cursor.fetchall():
                        salary_info = ""
                        if row[2] or row[3]:
                            if row[2] and row[3]:
                                salary_info = f"{row[2]} - {row[3]} {row[4]}"
                            elif row[2]:
                                salary_info = f"от {row[2]} {row[4]}"
                            elif row[3]:
                                salary_info = f"до {row[3]} {row[4]}"

                        result.append({
                            'company': row[0],
                            'vacancy': row[1],
                            'salary': salary_info,
                            'url': row[5]
                        })
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
        finally:
            self.disconnect()
        return result

    def get_avg_salary(self) -> float:
        """
        Получить среднюю зарплату по вакансиям

        Returns:
            float: средняя зарплата
        """
        self.connect()
        result: float = 0.0
        try:
            if self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2)
                        FROM vacancies
                        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                    """)
                    row = cursor.fetchone()
                    if row and row[0]:
                        result = round(float(row[0]), 2)
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
        finally:
            self.disconnect()
        return result

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """
        Получить список всех вакансий, у которых зарплата выше средней по всем вакансиям

        Returns:
            List[Dict]: список словарей с вакансиями
        """
        avg_salary = self.get_avg_salary()
        self.connect()
        result: List[Dict[str, Any]] = []
        try:
            if self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT
                            e.name as company_name,
                            v.name as vacancy_name,
                            v.salary_from,
                            v.salary_to,
                            v.currency,
                            v.alternate_url
                        FROM vacancies v
                        JOIN employers e ON v.employer_id = e.id
                        WHERE (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2 > %s
                        ORDER BY (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2 DESC
                    """, (avg_salary,))

                    for row in cursor.fetchall():
                        salary_info = ""
                        if row[2] or row[3]:
                            if row[2] and row[3]:
                                salary_info = f"{row[2]} - {row[3]} {row[4]}"
                            elif row[2]:
                                salary_info = f"от {row[2]} {row[4]}"
                            elif row[3]:
                                salary_info = f"до {row[3]} {row[4]}"

                        result.append({
                            'company': row[0],
                            'vacancy': row[1],
                            'salary': salary_info,
                            'url': row[5]
                        })
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
        finally:
            self.disconnect()
        return result

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получить список всех вакансий, в названии которых содержатся переданные слова

        Args:
            keyword: ключевое слово для поиска

        Returns:
            List[Dict]: список словарей с вакансиями
        """
        self.connect()
        result: List[Dict[str, Any]] = []
        try:
            if self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT
                            e.name as company_name,
                            v.name as vacancy_name,
                            v.salary_from,
                            v.salary_to,
                            v.currency,
                            v.alternate_url
                        FROM vacancies v
                        JOIN employers e ON v.employer_id = e.id
                        WHERE LOWER(v.name) LIKE %s
                        ORDER BY e.name, v.name
                    """, (f'%{keyword.lower()}%',))

                    for row in cursor.fetchall():
                        salary_info = ""
                        if row[2] or row[3]:
                            if row[2] and row[3]:
                                salary_info = f"{row[2]} - {row[3]} {row[4]}"
                            elif row[2]:
                                salary_info = f"от {row[2]} {row[4]}"
                            elif row[3]:
                                salary_info = f"до {row[3]} {row[4]}"

                        result.append({
                            'company': row[0],
                            'vacancy': row[1],
                            'salary': salary_info,
                            'url': row[5]
                        })
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
        finally:
            self.disconnect()
        return result
