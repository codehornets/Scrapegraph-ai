from pydantic import BaseModel


class MarketingGoal(BaseModel):
    goal: str
    description: str
    target_audience: str
