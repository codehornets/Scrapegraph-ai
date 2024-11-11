from typing import List
from pydantic import BaseModel

from src.models.email import Email


class EmailWorkflow(BaseModel):
    campaign_name: str
    description: str
    emails: List[Email] = []
