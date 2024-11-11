from typing import List, Optional

from pydantic import BaseModel


class CompanyCulture(BaseModel):
    core_values: List[str] = []
    employee_benefits: List[str] = []
    diversity_and_inclusion: Optional[str]
