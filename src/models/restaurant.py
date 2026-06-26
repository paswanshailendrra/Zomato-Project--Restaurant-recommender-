from pydantic import BaseModel
from typing import Literal, Optional, List

class Restaurant(BaseModel):
    id: int
    name: str
    location: str
    cuisines: List[str]
    rating: float
    cost_for_two: Optional[int] = None
    budget_tier: Literal["low", "medium", "high", "very high"]
    votes: Optional[int] = None
