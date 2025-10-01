import pytest
from unittest.mock import Mock, patch
from src.models import Salary
from src.db_manager import DBManager


class TestSalaryPytest:
    """Тесты для Salary с использованием pytest"""

    def test_salary_avg_calculation(self):
        """Тест расчета средней зарплаты с pytest"""
        salary = Salary(from_=100000, to=150000)
        assert salary.get_avg_salary() == 125000

    @pytest.mark.parametrize("from_salary,to_salary,expected_avg", [
        (100000, 150000, 125000),
        (100000, None, 100000),
        (None, 150000, 150000),
        (None, None, None)
    ])
    def test_salary_avg_variations(self, from_salary, to_salary, expected_avg):
        """Параметризованный тест различных вариантов зарплаты"""
        salary = Salary(from_=from_salary, to=to_salary)
        assert salary.get_avg_salary() == expected_avg


class TestDBManagerPytest:
    """Тесты для DBManager с использованием pytest"""

    @pytest.fixture
    def db_manager(self, mock_db_config):
        """Фикстура для DBManager"""
        manager = DBManager()
        manager.config = mock_db_config
        return manager

    def test_connection_management(self, db_manager):
        """Тест управления подключением"""
        with patch('psycopg2.connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn

            db_manager.connect()

            mock_connect.assert_called_once_with(**db_manager.config)
            assert db_manager.connection == mock_conn

    def test_disconnect(self, db_manager):
        """Тест отключения от БД"""
        mock_conn = Mock()
        db_manager.connection = mock_conn

        db_manager.disconnect()

        mock_conn.close.assert_called_once()
        assert db_manager.connection is None

    @patch('src.db_manager.DBManager.connect')
    @patch('src.db_manager.DBManager.disconnect')
    def test_get_companies_vacancies_count_empty(self, mock_disconnect, mock_connect, db_manager):
        """Тест получения компаний при пустой БД"""
        mock_conn = Mock()
        mock_cursor = Mock()
        db_manager.connection = mock_conn
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)

        mock_cursor.fetchall.return_value = []

        result = db_manager.get_companies_and_vacancies_count()

        assert result == []
        mock_disconnect.assert_called_once()
