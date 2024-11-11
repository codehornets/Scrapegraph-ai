from typing import Optional

from pydantic import BaseModel


class CompanyHeadquarter(BaseModel):
    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    country: Optional[str]
