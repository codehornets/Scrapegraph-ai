from typing import Optional
from pydantic import BaseModel


class Affiliates(BaseModel):
    partner_name: Optional[str]
    description: Optional[str]
    url: Optional[str]
