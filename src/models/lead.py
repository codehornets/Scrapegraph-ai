from typing import Dict, Optional
from pydantic import BaseModel


class Lead(BaseModel):
    query: Optional[str]
    scraper_name: Optional[str]
    results: Optional[Dict]
    filename: Optional[str]

    class Config:
        arbitrary_types_allowed = True
