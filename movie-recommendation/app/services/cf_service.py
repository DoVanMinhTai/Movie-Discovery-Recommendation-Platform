from typing import List, Any, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.recommendation import (
    PersonalizedResponse,
    RecommendationItem,
    SimilarUsersResponse,
    UserRecommendationRequest
)
from app.constants.cf_queries import CollaborativeQueries, CFStrategy
from app.models.user import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollaborativeService:
    def __init__(self, db: Session):
        self.db = db
    
    def _execute_query(self, query_str: str, params: dict) -> List[Any]:
        return self.db.execute(text(query_str), params).fetchall()

    def _map_to_recommendations(self, rows: List[Any]) -> List[RecommendationItem]:
        return [
            RecommendationItem(
                movie_id=r.movie_id,
                title=r.title,
                genres=r.genres,
                score=float(r.score)
            ) for r in rows
        ]

    async def _validate_user_exists(self, user_id: int):
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

    async def get_user_recommendations(self, user_id: int, top_n: int = 10) -> PersonalizedResponse:
        await self._validate_user_exists(user_id)
        
        rows = self._execute_query(
            CollaborativeQueries.USER_RECOMMENDATIONS, 
            {"user_id": user_id, "top_n": top_n}
        )
        
        return PersonalizedResponse(
            strategy=CFStrategy.COLLABORATIVE,
            recommendations=self._map_to_recommendations(rows)
        )
    
    async def get_item_based_similar(self, movie_id: int, top_n: int = 10) -> PersonalizedResponse:
        rows = self._execute_query(
            CollaborativeQueries.ITEM_SIMILAR, 
            {"movie_id": movie_id, "top_n": top_n}
        )
        
        return PersonalizedResponse(
            strategy=CFStrategy.ITEM_BASED,
            recommendations=self._map_to_recommendations(rows)
        )
    
    async def get_similar_users(self, user_id: int, top_n: int = 5) -> SimilarUsersResponse:
        rows = self._execute_query(
            CollaborativeQueries.SIMILAR_USERS, 
            {"user_id": user_id, "top_n": top_n}
        )
        
        similar_users = [
            {"user_id": r.user_id, "similarity": float(r.score)} 
            for r in rows
        ]
        
        return SimilarUsersResponse(user_id=user_id, similar_users=similar_users)

    async def handle_cold_start(self, request: UserRecommendationRequest) -> PersonalizedResponse:
        rows = self._execute_query(
            CollaborativeQueries.COLD_START_POPULAR, 
            {"top_n": request.top_n}
        )
        
        return PersonalizedResponse(
            strategy=CFStrategy.COLD_START,
            recommendations=self._map_to_recommendations(rows)
        )