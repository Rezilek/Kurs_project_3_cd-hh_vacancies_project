import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Добавляем корень проекта в путь Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import DatabaseManager
from src.models import Employer, Vacancy, Salary


class TestDatabaseIntegration(unittest.TestCase):
    """Интеграционные тесты для работы с базой данных"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.db_manager = DatabaseManager()
        self.db_manager.config = {
            'host': 'localhost',
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_password',
            'port': '5432'
        }

    @patch('psycopg2.connect')
    def test_create_tables(self, mock_connect):
        """Тест создания таблиц"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)

        self.db_manager.connection = mock_conn
        self.db_manager.create_tables()

        # Проверяем, что execute вызывался хотя бы один раз
        self.assertTrue(mock_cursor.execute.called)
        mock_conn.commit.assert_called_once()

    @patch('psycopg2.connect')
    def test_insert_employer(self, mock_connect):
        """Тест вставки работодателя"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)

        employer = Employer(
            id=123,
            name='Test Company',
            url='http://test.com',
            alternate_url='http://hh.ru/company/123',
            description='Test description'
        )

        self.db_manager.connection = mock_conn
        self.db_manager.insert_employer(employer)

        # Проверяем, что был хотя бы один вызов execute
        self.assertTrue(mock_cursor.execute.called)
        mock_conn.commit.assert_called_once()

    @patch('psycopg2.connect')
    def test_insert_vacancy(self, mock_connect):
        """Тест вставки вакансии"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)

        salary = Salary(from_=100000, to=150000, currency='RUR')
        vacancy = Vacancy(
            id=1,
            name='Test Vacancy',
            url='http://test.com/vacancy/1',
            alternate_url='http://hh.ru/vacancy/1',
            employer_id=123,
            salary=salary
        )

        self.db_manager.connection = mock_conn
        self.db_manager.insert_vacancy(vacancy)

        self.assertTrue(mock_cursor.execute.called)
        mock_conn.commit.assert_called_once()

    @patch('src.database.DatabaseManager.insert_employer')
    @patch('src.database.DatabaseManager.insert_vacancy')
    def test_load_data(self, mock_insert_vacancy, mock_insert_employer):
        """Тест загрузки данных"""
        employers = [
            Employer(id=1, name='Company A', url='', alternate_url=''),
            Employer(id=2, name='Company B', url='', alternate_url='')
        ]

        vacancies = [
            Vacancy(id=1, name='Vacancy 1', url='', alternate_url='', employer_id=1),
            Vacancy(id=2, name='Vacancy 2', url='', alternate_url='', employer_id=2)
        ]

        self.db_manager.load_data(employers, vacancies)

        self.assertEqual(mock_insert_employer.call_count, 2)
        self.assertEqual(mock_insert_vacancy.call_count, 2)


if __name__ == '__main__':
    unittest.main()