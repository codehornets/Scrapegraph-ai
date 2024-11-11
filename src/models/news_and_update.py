from typing import Optional
from pydantic import BaseModel


class NewsAndUpdates(BaseModel):
    title: Optional[str]
    description: Optional[str]
    date: Optional[str]
    url: Optional[str]
