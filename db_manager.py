import psycopg2
from typing import List, Dict, Any
from config import get_db_config


class DBManager:
    """Класс для работы с данными в БД PostgreSQL"""

    def __init__(self, config_file: str = 'config/database.ini'):
        self.config = get_db_config(config_file)
        self.connection = None

    def connect(self) -> None:
        try:
            self.connection = psycopg2.connect(**self.config)
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise

    def disconnect(self) -> None:
        if self.connection:
            self.connection.close()

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT e.name, COUNT(v.id) as vacancy_count
                    FROM employers e
                    LEFT JOIN vacancies v ON e.id = v.employer_id
                    GROUP BY e.id, e.name
                    ORDER BY vacancy_count DESC
                """)
                result = []
                for row in cursor.fetchall():
                    result.append({
                        'company': row[0],
                        'vacancies_count': row[1]
                    })
                return result
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []
        finally:
            self.disconnect()

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT e.name, v.name, v.salary_from, v.salary_to, v.currency, v.alternate_url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.id
                    ORDER BY e.name, v.name
                """)
                result = []
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
                return result
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []
        finally:
            self.disconnect()

    def get_avg_salary(self) -> float:
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2)
                    FROM vacancies
                    WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                """)
                result = cursor.fetchone()[0]
                return round(float(result), 2) if result else 0.0
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return 0.0
        finally:
            self.disconnect()

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        avg_salary = self.get_avg_salary()
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT e.name, v.name, v.salary_from, v.salary_to, v.currency, v.alternate_url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.id
                    WHERE (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2 > %s
                    ORDER BY (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2 DESC
                """, (avg_salary,))

                result = []
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
                return result
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []
        finally:
            self.disconnect()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT e.name, v.name, v.salary_from, v.salary_to, v.currency, v.alternate_url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.id
                    WHERE LOWER(v.name) LIKE %s
                    ORDER BY e.name, v.name
                """, (f'%{keyword.lower()}%',))

                result = []
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
                return result
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []
        finally:
            self.disconnect()
