from typing import Optional

from pydantic import BaseModel, Field


class SimilaritySearch(BaseModel):
    query: str
    limit: int
    score_threshold: float
    filters: Optional[dict] = Field(default=None)