from pydantic import BaseModel


class ScoredHighlight(BaseModel):
    start: float
    end: float
    score: int
    reason: str
    hook_score: int = 0
    viral_score: int = 0
    duration_score: int = 0
    total_score: int = 0
    rank: int = 0