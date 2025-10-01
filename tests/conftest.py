import pytest
import sys
import os

# Добавляем путь к исходному коду
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def sample_employer():
    """Фикстура для тестового работодателя"""
    from src.models import Employer
    return Employer(
        id=123,
        name='Test Company',
        url='http://test.com',
        alternate_url='http://hh.ru/company/123',
        description='Test description'
    )


@pytest.fixture
def sample_vacancy():
    """Фикстура для тестовой вакансии"""
    from src.models import Vacancy, Salary
    salary = Salary(from_=100000, to=150000, currency='RUR')
    return Vacancy(
        id=1,
        name='Test Vacancy',
        url='http://test.com/vacancy/1',
        alternate_url='http://hh.ru/vacancy/1',
        employer_id=123,
        salary=salary,
        description='Test description'
    )


@pytest.fixture
def mock_db_config():
    """Фикстура для мок-конфигурации БД"""
    return {
        'host': 'localhost',
        'database': 'test_db',
        'user': 'test_user',
        'password': 'test_password',
        'port': '5432'
    }
