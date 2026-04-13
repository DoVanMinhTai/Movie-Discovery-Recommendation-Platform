from elasticsearch import AsyncElasticsearch
from app.config.config import settings

class SearchService:
    def __init__(self):
        self.es_client = AsyncElasticsearch(hosts=settings.es_host,     
        headers={"Accept": "application/json", "Content-Type": "application/json"})

    async def search_movies(self, params: dict):
        must_queries = []
        field_mapping = {"title": "title", "director": "director_name", "genre": "genres", "year": "releaseDate"}

        for key, value in params.items():
            if value and key in field_mapping:
                must_queries.append({
                    "match": {field_mapping[key]: 
                    {
                            "query": value,
                            "fuzziness": 1,
                            "operator": "or"
                        }}})
    
        query = {
            "query": {"bool": {"must": must_queries if must_queries else [{"match_all": {}}]}},
            "size": 5
        }
        try:
            res =  await self.es_client.search(index="mediacontent", body=query)
            return [hit["_source"] for hit in res["hits"]["hits"]]
        except Exception as e:
            print(f"ES Error: {e}")
            return []
        
    async def fall_Back_ElasticSearch(self, movie_name: str):
        """Tìm kiếm mờ khi không tìm thấy tên phim chính xác"""
        query = {
            "query": {
                "match": { "title": { "query": movie_name, "fuzziness": "AUTO" } }
            },
            "_source": ["id"],
            "size": 3
        }
        try:
            res = await self.es_client.search(index="movies", body=query)
            return [hit["_source"]["id"] for hit in res["hits"]["hits"]]
        except Exception as e:
            print(f"Fallback ES Error: {e}")
        return []
    
    async def find_movie_id_by_name(self, movie_name: str):
        query = {
            "query": {
                "match_phrase": { "title": movie_name }
            },
            "_source": ["id"],
            "size": 1
        }
        try:
            res = await self.es_client.search(index="movies", body=query)
            hits = res["hits"]["hits"]
            if hits:
                return hits[0]["_source"]["id"]
        except Exception as e:
            print(f"Error finding movie ID: {e}")
        return None

    