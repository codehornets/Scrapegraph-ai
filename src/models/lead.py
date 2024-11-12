from typing import Dict, Optional
from pydantic import BaseModel


class Lead(BaseModel):
    query: Optional[str]
    keyword: Optional[str]
    intent: Optional[str]
    score: Optional[float]
    scraper_name: Optional[str]
    filename: Optional[str]
    results: Optional[Dict]

    class Config:
        arbitrary_types_allowed = True
