import unittest
import sys
import os
from unittest.mock import Mock, patch


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.db_manager import DBManager


class TestDBManager(unittest.TestCase):
    """Тесты для класса DBManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.db_manager = DBManager()
        self.db_manager.config = {
            'host': 'localhost',
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_password',
            'port': '5432'
        }

    @patch('psycopg2.connect')
    def test_connect_success(self, mock_connect):
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        self.db_manager.connect()

        # Проверяем, что connect был вызван с любыми аргументами
        mock_connect.assert_called_once()
        # Или проверяем конкретные аргументы, которые реально использует ваш код
        mock_connect.assert_called_once_with(
            host='localhost',
            database='test_db',
            user='test_user',
            password='test_password',
            port='5432'
        )
        self.assertEqual(self.db_manager.connection, mock_conn)

    @patch('psycopg2.connect')
    def test_connect_failure(self, mock_connect):
        """Тест неудачного подключения к БД"""
        mock_connect.side_effect = Exception("Connection failed")

        with self.assertRaises(Exception):
            self.db_manager.connect()

    def test_disconnect(self):
        """Тест отключения от БД"""
        mock_conn = Mock()
        self.db_manager.connection = mock_conn

        self.db_manager.disconnect()

        mock_conn.close.assert_called_once()
        self.assertIsNone(self.db_manager.connection)

    def test_disconnect_no_connection(self):
        """Тест отключения при отсутствии соединения"""
        self.db_manager.connection = None

        # Не должно вызывать ошибку
        self.db_manager.disconnect()

    @patch('src.db_manager.DBManager.connect')
    @patch('src.db_manager.DBManager.disconnect')
    def test_get_companies_and_vacancies_count(self, mock_disconnect, mock_connect):
        """Тест получения компаний и количества вакансий"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = None
        self.db_manager.connection = mock_conn
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)

        mock_cursor.fetchall.return_value = [
            ('Company A', 5),
            ('Company B', 3)
        ]

        result = self.db_manager.get_companies_and_vacancies_count()

        expected_result = [
            {'company': 'Company A', 'vacancies_count': 5},
            {'company': 'Company B', 'vacancies_count': 3}
        ]

        self.assertEqual(result, expected_result)
        mock_disconnect.assert_called_once()

    @patch('src.db_manager.DBManager.connect')
    @patch('src.db_manager.DBManager.disconnect')
    def test_get_all_vacancies(self, mock_disconnect, mock_connect):
        """Тест получения всех вакансий"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = None
        self.db_manager.connection = mock_conn
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)

        mock_cursor.fetchall.return_value = [
            ('Company A', 'Python Dev', 100000, 150000, 'RUR', 'http://example.com/1'),
            ('Company B', 'Java Dev', None, 200000, 'RUR', 'http://example.com/2')
        ]

        result = self.db_manager.get_all_vacancies()

        expected_result = [
            {
                'company': 'Company A',
                'vacancy': 'Python Dev',
                'salary': '100000 - 150000 RUR',
                'url': 'http://example.com/1'
            },
            {
                'company': 'Company B',
                'vacancy': 'Java Dev',
                'salary': 'до 200000 RUR',
                'url': 'http://example.com/2'
            }
        ]

        self.assertEqual(result, expected_result)
        mock_disconnect.assert_called_once()

    @patch('src.db_manager.DBManager.connect')
    @patch('src.db_manager.DBManager.disconnect')
    def test_get_avg_salary(self, mock_disconnect, mock_connect):
        """Тест получения средней зарплаты"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = None
        self.db_manager.connection = mock_conn
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)

        mock_cursor.fetchone.return_value = (125000.50,)

        result = self.db_manager.get_avg_salary()

        self.assertEqual(result, 125000.50)
        mock_disconnect.assert_called_once()

    @patch('src.db_manager.DBManager.get_avg_salary')
    @patch('src.db_manager.DBManager.connect')
    @patch('src.db_manager.DBManager.disconnect')
    def test_get_vacancies_with_higher_salary(self, mock_disconnect, mock_connect, mock_avg_salary):
        """Тест получения вакансий с зарплатой выше средней"""
        mock_avg_salary.return_value = 100000
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = None
        self.db_manager.connection = mock_conn
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)

        mock_cursor.fetchall.return_value = [
            ('Company A', 'Senior Dev', 150000, 200000, 'RUR', 'http://example.com/1')
        ]

        result = self.db_manager.get_vacancies_with_higher_salary()

        expected_result = [
            {
                'company': 'Company A',
                'vacancy': 'Senior Dev',
                'salary': '150000 - 200000 RUR',
                'url': 'http://example.com/1'
            }
        ]

        self.assertEqual(result, expected_result)
        mock_avg_salary.assert_called_once()
        mock_disconnect.assert_called_once()

    @patch('src.db_manager.DBManager.connect')
    @patch('src.db_manager.DBManager.disconnect')
    def test_get_vacancies_with_keyword(self, mock_disconnect, mock_connect):
        """Тест поиска вакансий по ключевому слову"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = None
        self.db_manager.connection = mock_conn
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)

        mock_cursor.fetchall.return_value = [
            ('Company A', 'Python Developer', 100000, 150000, 'RUR', 'http://example.com/1')
        ]

        result = self.db_manager.get_vacancies_with_keyword('python')

        expected_result = [
            {
                'company': 'Company A',
                'vacancy': 'Python Developer',
                'salary': '100000 - 150000 RUR',
                'url': 'http://example.com/1'
            }
        ]

        self.assertEqual(result, expected_result)
        mock_disconnect.assert_called_once()

    @patch('src.db_manager.DBManager.connect')
    @patch('src.db_manager.DBManager.disconnect')
    def test_get_vacancies_with_keyword_no_results(self, mock_disconnect, mock_connect):
        """Тест поиска вакансий по ключевому слову без результатов"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = None
        self.db_manager.connection = mock_conn
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)

        mock_cursor.fetchall.return_value = []

        result = self.db_manager.get_vacancies_with_keyword('nonexistent')

        self.assertEqual(result, [])
        mock_disconnect.assert_called_once()


if __name__ == '__main__':
    unittest.main()
