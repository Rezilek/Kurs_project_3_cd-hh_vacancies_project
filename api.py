import requests
from typing import Dict, List, Any, Optional


class HHAPI:
    """Класс для взаимодействия с API HeadHunter"""

    BASE_URL = "https://api.hh.ru/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HH-Vacancies-API/1.0'
        })

    def get_employer(self, employer_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о работодателе по ID
        """
        url = f"{self.BASE_URL}employers/{employer_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при получении данных работодателя {employer_id}: {e}")
            return None

    def get_vacancies(self, employer_id: int, page: int = 0, per_page: int = 100) -> Optional[Dict[str, Any]]:
        """
        Получить вакансии работодателя
        """
        url = f"{self.BASE_URL}vacancies"
        params = {
            'employer_id': employer_id,
            'page': page,
            'per_page': per_page
        }

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при получении вакансий работодателя {employer_id}: {e}")
            return None

    def get_all_vacancies(self, employer_id: int) -> List[Dict[str, Any]]:
        """
        Получить все вакансии работодателя
        """
        all_vacancies = []
        page = 0

        while True:
            data = self.get_vacancies(employer_id, page)
            if not data:
                break

            vacancies = data.get('items', [])
            if not vacancies:
                break

            all_vacancies.extend(vacancies)

            pages = data.get('pages', 0)
            if page >= pages - 1:
                break

            page += 1

        return all_vacancies


def get_employer_data(api: HHAPI, employer_ids: List[int]) -> Dict[int, Dict]:
    """
    Получить данные о работодателях
    """
    employers = {}
    for emp_id in employer_ids:
        employer_data = api.get_employer(emp_id)
        if employer_data:
            employers[emp_id] = employer_data
            print(f"Получены данные работодателя: {employer_data['name']}")
    return employers


def get_vacancies_data(api: HHAPI, employer_ids: List[int]) -> Dict[int, List[Dict]]:
    """
    Получить вакансии для всех работодателей
    """
    vacancies = {}
    for emp_id in employer_ids:
        emp_vacancies = api.get_all_vacancies(emp_id)
        vacancies[emp_id] = emp_vacancies
        print(f"Получено {len(emp_vacancies)} вакансий для работодателя {emp_id}")
    return vacancies

