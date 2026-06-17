from elasticsearch import AsyncElasticsearch
import logging
from app.core.config import settings

logger = logging.getLogger("SearchService")

class SearchService:
    def __init__(self):
        self.es = AsyncElasticsearch(
            settings.es_host,
            headers={'Content-Type': 'application/json'}
        )
        self.index_name = "movies_cbf" 

    async def search_movies(self, query: str, limit: int = 5):
        try:
            search_body = {
                "size": limit,
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "director", "actors", "description"],
                        "fuzziness": "AUTO"
                    }
                }
            }
            
            response = await self.es.search(index=self.index_name, body=search_body)
            hits = response['hits']['hits']
            
            results = []
            for hit in hits:
                source = hit['_source']
                results.append({
                    "id": hit['_id'],
                    "title": source.get('title'),
                    "slug": source.get('slug'),
                    "thumbnail_url": source.get('poster_path'), 
                    "rating": source.get('vote_average')
                })
            return results
        except Exception as e:
            logger.error(f"Error searching Elasticsearch: {e}")
            return []

    async def find_movie_id_by_name(self, movie_name: str):
        results = await self.search_movies(movie_name, limit=1)
        return results[0]['id'] if results else None
