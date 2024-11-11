from typing import Optional

from pydantic import BaseModel


class CSRInitiatives(BaseModel):
    initiative_name: Optional[str]
    description: Optional[str]
    url: Optional[str]
