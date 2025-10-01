import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models import Employer, Vacancy, Salary


class TestSalary(unittest.TestCase):
    """Тесты для класса Salary"""

    def test_salary_creation(self):
        """Тест создания объекта Salary"""
        salary = Salary(from_=100000, to=150000, currency='RUR', gross=True)

        self.assertEqual(salary.from_, 100000)
        self.assertEqual(salary.to, 150000)
        self.assertEqual(salary.currency, 'RUR')
        self.assertEqual(salary.gross, True)

    def test_get_avg_salary_both_values(self):
        """Тест расчета средней зарплаты при наличии from и to"""
        salary = Salary(from_=100000, to=150000)
        avg_salary = salary.get_avg_salary()

        self.assertEqual(avg_salary, 125000)

    def test_get_avg_salary_only_from(self):
        """Тест расчета средней зарплаты при наличии только from"""
        salary = Salary(from_=100000)
        avg_salary = salary.get_avg_salary()

        self.assertEqual(avg_salary, 100000)

    def test_get_avg_salary_only_to(self):
        """Тест расчета средней зарплаты при наличии только to"""
        salary = Salary(to=150000)
        avg_salary = salary.get_avg_salary()

        self.assertEqual(avg_salary, 150000)

    def test_get_avg_salary_no_values(self):
        """Тест расчета средней зарплаты при отсутствии значений"""
        salary = Salary()
        avg_salary = salary.get_avg_salary()

        self.assertIsNone(avg_salary)


class TestEmployer(unittest.TestCase):
    """Тесты для класса Employer"""

    def test_employer_creation(self):
        """Тест создания объекта Employer"""
        employer = Employer(
            id=123,
            name='Test Company',
            url='http://test.com',
            alternate_url='http://hh.ru/company/123',
            description='Test description'
        )

        self.assertEqual(employer.id, 123)
        self.assertEqual(employer.name, 'Test Company')
        self.assertEqual(employer.url, 'http://test.com')
        self.assertEqual(employer.alternate_url, 'http://hh.ru/company/123')
        self.assertEqual(employer.description, 'Test description')

    def test_employer_from_json(self):
        """Тест создания Employer из JSON"""
        json_data = {
            'id': 456,
            'name': 'JSON Company',
            'url': 'http://json.com',
            'alternate_url': 'http://hh.ru/company/456',
            'description': 'JSON description'
        }

        employer = Employer.from_json(json_data)

        self.assertEqual(employer.id, 456)
        self.assertEqual(employer.name, 'JSON Company')
        self.assertEqual(employer.url, 'http://json.com')
        self.assertEqual(employer.alternate_url, 'http://hh.ru/company/456')
        self.assertEqual(employer.description, 'JSON description')

    def test_employer_from_json_optional_fields(self):
        """Тест создания Employer из JSON с опциональными полями"""
        json_data = {
            'id': 789,
            'name': 'Minimal Company',
            'url': '',
            'alternate_url': ''
        }

        employer = Employer.from_json(json_data)

        self.assertEqual(employer.id, 789)
        self.assertEqual(employer.name, 'Minimal Company')
        self.assertEqual(employer.url, '')
        self.assertEqual(employer.alternate_url, '')
        self.assertIsNone(employer.description)


class TestVacancy(unittest.TestCase):
    """Тесты для класса Vacancy"""

    def test_vacancy_creation(self):
        """Тест создания объекта Vacancy"""
        salary = Salary(from_=100000, to=150000)
        vacancy = Vacancy(
            id=1,
            name='Python Developer',
            url='http://test.com/vacancy/1',
            alternate_url='http://hh.ru/vacancy/1',
            employer_id=123,
            salary=salary,
            description='Test vacancy',
            experience='1-3 years',
            employment='full'
        )

        self.assertEqual(vacancy.id, 1)
        self.assertEqual(vacancy.name, 'Python Developer')
        self.assertEqual(vacancy.employer_id, 123)
        self.assertEqual(vacancy.salary, salary)
        self.assertEqual(vacancy.description, 'Test vacancy')
        self.assertEqual(vacancy.experience, '1-3 years')
        self.assertEqual(vacancy.employment, 'full')

    def test_vacancy_from_json_with_salary(self):
        """Тест создания Vacancy из JSON с зарплатой"""
        json_data = {
            'id': 2,
            'name': 'Java Developer',
            'url': 'http://test.com/vacancy/2',
            'alternate_url': 'http://hh.ru/vacancy/2',
            'employer': {'id': 456},
            'salary': {
                'from': 120000,
                'to': 180000,
                'currency': 'RUR',
                'gross': True
            },
            'description': 'Java vacancy',
            'experience': {'name': '3-6 years'},
            'employment': {'name': 'part'}
        }

        vacancy = Vacancy.from_json(json_data)

        self.assertEqual(vacancy.id, 2)
        self.assertEqual(vacancy.name, 'Java Developer')
        self.assertEqual(vacancy.employer_id, 456)
        self.assertIsNotNone(vacancy.salary)
        self.assertEqual(vacancy.salary.from_, 120000)
        self.assertEqual(vacancy.salary.to, 180000)
        self.assertEqual(vacancy.salary.currency, 'RUR')
        self.assertEqual(vacancy.description, 'Java vacancy')
        self.assertEqual(vacancy.experience, '3-6 years')
        self.assertEqual(vacancy.employment, 'part')

    def test_vacancy_from_json_without_salary(self):
        """Тест создания Vacancy из JSON без зарплаты"""
        json_data = {
            'id': 3,
            'name': 'Frontend Developer',
            'url': '',
            'alternate_url': 'http://hh.ru/vacancy/3',
            'employer': {'id': 789},
            'description': 'Frontend vacancy'
        }

        vacancy = Vacancy.from_json(json_data)

        self.assertEqual(vacancy.id, 3)
        self.assertEqual(vacancy.name, 'Frontend Developer')
        self.assertEqual(vacancy.employer_id, 789)
        self.assertIsNone(vacancy.salary)
        self.assertEqual(vacancy.description, 'Frontend vacancy')
        self.assertIsNone(vacancy.experience)
        self.assertIsNone(vacancy.employment)


if __name__ == '__main__':
    unittest.main()
    