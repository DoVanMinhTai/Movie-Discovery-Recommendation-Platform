from pydantic import BaseModel
from typing import List, Optional

class RecommendationItem(BaseModel):
    movie_id: int
    score: float
    title: Optional[str] = None
    poster_path: Optional[str] = None
    slug: Optional[str] = None

class RecommendationResponse(BaseModel):
    strategy: str
    data: List[RecommendationItem]

class UserContext(BaseModel):
    user_id: Optional[int] = None
    selected_genres: Optional[List[str]] = None
    is_new_user: bool = True
