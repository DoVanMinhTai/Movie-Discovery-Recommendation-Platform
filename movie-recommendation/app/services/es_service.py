from elasticsearch import AsyncElasticsearch
from app.core.config import settings
import logging

logger = logging.getLogger("EsService")



class EsService:
    def __init__(self, client: AsyncElasticsearch):
        self.client = client
        self.index_name = "mediacontent"

    async def get_movie_by_id(self, movie_id: int):
        try:
            query = {
                "query": {
                    "term": {
                        "id": movie_id
                    }
                }
            }
            response = await self.client.search(index=self.index_name, body=query)

            hits = response.get('hits', {}).get('hits', [])
            
            if hits:
                source = hits[0].get('_source', {})
                return {
                    "title": source.get('title'),
                    "poster_path": source.get('poster_path'),
                    "slug": source.get('slug')
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching movie metadata for ID {movie_id}: {e}")
            return None
