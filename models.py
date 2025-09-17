from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Employer:
    """Модель работодателя"""
    id: int
    name: str
    url: str
    alternate_url: str
    description: Optional[str] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Employer':
        return cls(
            id=data['id'],
            name=data['name'],
            url=data.get('url', ''),
            alternate_url=data.get('alternate_url', ''),
            description=data.get('description')
        )


@dataclass
class Salary:
    """Модель зарплаты"""
    from_: Optional[int] = None
    to: Optional[int] = None
    currency: Optional[str] = None

    def get_avg_salary(self) -> Optional[float]:
        if self.from_ is not None and self.to is not None:
            return (self.from_ + self.to) / 2
        elif self.from_ is not None:
            return self.from_
        elif self.to is not None:
            return self.to
        return None


@dataclass
class Vacancy:
    """Модель вакансии"""
    id: int
    name: str
    url: str
    alternate_url: str
    employer_id: int
    salary: Optional[Salary] = None
    description: Optional[str] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Vacancy':
        salary_data = data.get('salary')
        salary = None
        if salary_data:
            salary = Salary(
                from_=salary_data.get('from'),
                to=salary_data.get('to'),
                currency=salary_data.get('currency')
            )

        return cls(
            id=data['id'],
            name=data['name'],
            url=data.get('url', ''),
            alternate_url=data.get('alternate_url', ''),
            employer_id=data['employer']['id'],
            salary=salary,
            description=data.get('description')
        )
    