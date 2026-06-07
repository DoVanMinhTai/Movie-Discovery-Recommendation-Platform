from opensearchpy import OpenSearch
from app.core.config import settings
import logging

logger = logging.getLogger("EsService")

def get_es_client() -> OpenSearch:
    hosts = [{"host": settings.ES_HOST, "port": 443}]
    auth = (settings.ES_USERNAME, settings.ES_PASSWORD)
    return OpenSearch(
        hosts=hosts,
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )

class EsService:
    def __init__(self, client: OpenSearch):
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
            response = self.client.search(index=self.index_name, body=query)
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
