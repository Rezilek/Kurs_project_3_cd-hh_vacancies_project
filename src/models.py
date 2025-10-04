from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Salary:
    """Модель зарплаты"""

    from_: Optional[int] = None
    to: Optional[int] = None
    currency: Optional[str] = None
    gross: Optional[bool] = None

    def get_avg_salary(self) -> Optional[float]:
        """Получить среднюю зарплату"""
        if self.from_ is not None and self.to is not None:
            return (self.from_ + self.to) / 2
        elif self.from_ is not None:
            return float(self.from_)
        elif self.to is not None:
            return float(self.to)
        return None


@dataclass
class Employer:
    """Модель работодателя"""

    id: int
    name: str
    url: str
    alternate_url: str
    description: Optional[str] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Employer":
        """Создать объект Employer из JSON данных"""
        return cls(
            id=int(data["id"]),
            name=data["name"],
            url=data.get("url", ""),
            alternate_url=data.get("alternate_url", ""),
            description=data.get("description"),
        )


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
    experience: Optional[str] = None
    employment: Optional[str] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Vacancy":
        """Создать объект Vacancy из JSON данных"""
        salary_data = data.get("salary")
        salary = None
        if salary_data:
            salary = Salary(
                from_=salary_data.get("from"),
                to=salary_data.get("to"),
                currency=salary_data.get("currency"),
                gross=salary_data.get("gross"),
            )

        return cls(
            id=int(data["id"]),
            name=data["name"],
            url=data.get("url", ""),
            alternate_url=data.get("alternate_url", ""),
            employer_id=int(data["employer"]["id"]),
            salary=salary,
            description=data.get("description"),
            experience=data.get("experience", {}).get("name"),
            employment=data.get("employment", {}).get("name"),
        )
