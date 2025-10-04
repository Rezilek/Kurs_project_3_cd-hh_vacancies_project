import unittest
from unittest.mock import patch

import requests_mock

from src.api import HHAPI, get_employer_data, get_vacancies_data


class TestHHAPI(unittest.TestCase):
    """Тесты для класса HHAPI"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.api = HHAPI()
        self.employer_id = 123
        self.mock_employer_data = {
            "id": self.employer_id,
            "name": "Test Company",
            "url": "http://test.com",
            "alternate_url": "http://hh.ru/company/123",
            "description": "Test description",
        }
        self.mock_vacancies_data = {
            "items": [
                {
                    "id": 1,
                    "name": "Python Developer",
                    "url": "http://test.com/vacancy/1",
                    "alternate_url": "http://hh.ru/vacancy/1",
                    "employer": {"id": self.employer_id},
                    "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                    "description": "Test description",
                }
            ],
            "pages": 1,
            "found": 1,
        }

    @requests_mock.Mocker()
    def test_get_employer_success(self, mock):
        """Тест успешного получения данных работодателя"""
        mock.get(
            f"https://api.hh.ru/employers/{self.employer_id}",
            json=self.mock_employer_data,
        )

        result = self.api.get_employer(self.employer_id)

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], self.employer_id)
        self.assertEqual(result["name"], "Test Company")

    @requests_mock.Mocker()
    def test_get_employer_failure(self, mock):
        """Тест неудачного получения данных работодателя"""
        mock.get(f"https://api.hh.ru/employers/{self.employer_id}", status_code=404)

        result = self.api.get_employer(self.employer_id)

        self.assertIsNone(result)

    @requests_mock.Mocker()
    def test_get_vacancies_success(self, mock):
        """Тест успешного получения вакансий"""
        mock.get("https://api.hh.ru/vacancies", json=self.mock_vacancies_data)

        result = self.api.get_vacancies(self.employer_id)

        self.assertIsNotNone(result)
        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["name"], "Python Developer")

    @requests_mock.Mocker()
    def test_get_vacancies_failure(self, mock):
        """Тест неудачного получения вакансий"""
        mock.get("https://api.hh.ru/vacancies", status_code=500)

        result = self.api.get_vacancies(self.employer_id)

        self.assertIsNone(result)

    @requests_mock.Mocker()
    def test_get_all_vacancies(self, mock):
        """Тест получения всех вакансий с пагинацией"""
        # Мокаем первую страницу
        mock.get(
            "https://api.hh.ru/vacancies",
            [
                {
                    "json": {
                        "items": [
                            {
                                "id": 1,
                                "name": "Vacancy 1",
                                "employer": {"id": self.employer_id},
                            }
                        ],
                        "pages": 2,
                    }
                },
                {
                    "json": {
                        "items": [
                            {
                                "id": 2,
                                "name": "Vacancy 2",
                                "employer": {"id": self.employer_id},
                            }
                        ],
                        "pages": 2,
                    }
                },
            ],
        )

        result = self.api.get_all_vacancies(self.employer_id)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[1]["id"], 2)

    @requests_mock.Mocker()
    def test_get_all_vacancies_empty(self, mock):
        """Тест получения всех вакансий при их отсутствии"""
        mock.get("https://api.hh.ru/vacancies", json={"items": [], "pages": 1})

        result = self.api.get_all_vacancies(self.employer_id)

        self.assertEqual(len(result), 0)


class TestAPIFunctions(unittest.TestCase):
    """Тесты для функций API модуля"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.api = HHAPI()
        self.employer_ids = [123, 456]

    @patch("src.api.HHAPI.get_employer")
    def test_get_employer_data(self, mock_get_employer):
        """Тест получения данных работодателей"""
        mock_get_employer.side_effect = [
            {"id": 123, "name": "Company A"},
            {"id": 456, "name": "Company B"},
        ]

        result = get_employer_data(self.api, self.employer_ids)

        self.assertEqual(len(result), 2)
        self.assertIn(123, result)
        self.assertIn(456, result)
        self.assertEqual(result[123]["name"], "Company A")
        self.assertEqual(result[456]["name"], "Company B")

    @patch("src.api.HHAPI.get_all_vacancies")
    def test_get_vacancies_data(self, mock_get_all_vacancies):
        """Тест получения данных вакансий"""
        mock_get_all_vacancies.side_effect = [
            [{"id": 1, "name": "Vacancy 1", "employer": {"id": 123}}],
            [{"id": 2, "name": "Vacancy 2", "employer": {"id": 456}}],
        ]

        result = get_vacancies_data(self.api, self.employer_ids)

        self.assertEqual(len(result), 2)
        self.assertIn(123, result)
        self.assertIn(456, result)
        self.assertEqual(len(result[123]), 1)
        self.assertEqual(len(result[456]), 1)


if __name__ == "__main__":
    unittest.main()
