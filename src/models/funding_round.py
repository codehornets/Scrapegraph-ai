from typing import List, Optional

from pydantic import BaseModel


class FundingRound(BaseModel):
    round: Optional[str]
    amount: Optional[str]
    investors: List[str] = []
