from typing import Optional

from pydantic import BaseModel


class CareerOpportunities(BaseModel):
    position: Optional[str]
    location: Optional[str]
    job_type: Optional[str]
    url: Optional[str]
