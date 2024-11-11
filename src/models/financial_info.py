from typing import List, Optional

from pydantic import BaseModel

from src.models.funding_round import FundingRound


class FinancialInformation(BaseModel):
    revenue: Optional[str]
    valuation: Optional[str]
    funding_rounds: List[FundingRound] = []
