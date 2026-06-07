import httpx
import logging
from app.config.config import settings

logger = logging.getLogger("RecommendationService")

class RecommendationService:
    def __init__(self):
        self.base_url = settings.recommendation_service_url 

    async def get_user_recommendations(self, user_id: int, top_n: int = 5):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/recommendations/cf/user-recommendations/{user_id}",
                    params={"top_n": top_n}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error calling CF recommendations: {e}")
            return []

    async def get_similar_movies(self, movie_id: int, top_n: int = 5):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/recommendations/cf/item-similarity/{movie_id}",
                    params={"top_n": top_n}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error calling similarity recommendations: {e}")
            return []

    async def get_hybrid_recommendations(self, user_id: int, top_n: int = 5):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/cf/user-recommendations/{user_id}",
                    params={"top_n": top_n}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error calling hybrid recommendations: {e}")
            return []
