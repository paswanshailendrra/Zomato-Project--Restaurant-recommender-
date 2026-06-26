from pydantic import BaseModel
from typing import Optional, List

class Recommendation(BaseModel):
    id: int
    rank: int
    name: str
    cuisines: List[str]
    rating: float
    estimated_cost: Optional[int] = None
    explanation: str

class RecommendationResponse(BaseModel):
    summary: Optional[str] = None
    recommendations: List[Recommendation]
