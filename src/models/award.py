from typing import Optional
from pydantic import BaseModel


class Awards(BaseModel):
    title: Optional[str]
    description: Optional[str]
    date: Optional[str]
    url: Optional[str]
