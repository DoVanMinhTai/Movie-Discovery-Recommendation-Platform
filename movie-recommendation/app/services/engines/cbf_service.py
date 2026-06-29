import logging
from typing import List, Optional, Dict, Any
from elasticsearch import AsyncElasticsearch, NotFoundError

from app.core.constants import SearchIndex, ESFields, QueryTemplates
from app.services.embed_service import EmbeddingProvider

logger = logging.getLogger(__name__)


class MovieNotFoundError(Exception):
    """Raised when a movie document cannot be found in Elasticsearch."""
    pass

class ContentBasedService:
    def __init__(self, es_client: AsyncElasticsearch, embedding_provider: EmbeddingProvider):
        self.es = es_client
        self.embedding_provider = embedding_provider
        self.index = SearchIndex.MOVIES

    async def _fetch_doc_by_id(self, doc_id: int, fields: List[str]) -> Dict[str, Any]:
        """Lấy thông tin một document đơn lẻ (Bất đồng bộ)."""
        try:
            res = await self.es.get(index=self.index, id=str(doc_id), source=fields)
            return res['_source']
        except NotFoundError:
            logger.warning(f"Doc {doc_id} not found in Elasticsearch.")
            return {}
        except Exception as e:
            logger.error(f"Error fetching doc {doc_id}: {e}")
            return {}

    async def _fetch_docs_by_ids(self, doc_ids: List[int], fields: List[str]) -> List[Dict[str, Any]]:
        """Tối ưu hóa: Lấy nhiều documents cùng lúc bằng mget để tránh nghẽn mạng."""
        if not doc_ids:
            return []
        try:
            res = await self.es.mget(
                index=self.index,
                ids=[str(mid) for mid in doc_ids],
                source=fields
            )
            return [doc['_source'] for doc in res['docs'] if doc.get('found')]
        except Exception as e:
            logger.error(f"Error multi-fetching docs {doc_ids}: {e}")
            return []

    def _format_hit(self, hit: Dict[str, Any]) -> Dict[str, Any]:
        """Format lại kết quả trả về gọn gàng."""
        source = hit['_source']
        return {
            "movie_id": source.get(ESFields.MOVIE_ID),
            "title": source.get(ESFields.TITLE),
            "genres": source.get(ESFields.GENRES, []),
            "score": float(hit['_score'])
        }
        
    async def find_similar_movies(
        self, 
        movie_id: int, 
        top_n: int = 10
    ) -> Dict[str, Any]:
        """Tìm kiếm các bộ phim tương đồng dựa trên Vector KNN."""
        try:
            movie_doc = await self._fetch_doc_by_id(movie_id, [ESFields.TITLE, ESFields.EMBEDDING])
            if not movie_doc:
                raise MovieNotFoundError(f"Movie {movie_id} not found")

            query = QueryTemplates.knn_search(
                vector=movie_doc[ESFields.EMBEDDING],
                k=top_n + 1,
                size=top_n + 1,
                source_fields=[ESFields.MOVIE_ID, ESFields.TITLE, ESFields.GENRES]
            )      
            results = await self.es.search(index=self.index, **query)
            
            recommendations = [
                self._format_hit(h) for h in results['hits']['hits'] 
                if h['_source'][ESFields.MOVIE_ID] != movie_id
            ]
            return {
                "movie_id": movie_id,
                "movie_title": movie_doc.get(ESFields.TITLE, "Unknown"),
                "recommendations": recommendations[:top_n]}     
        except Exception as e:
            logger.error(f"Error finding similar movies for {movie_id}: {e}")
            raise

    async def get_personalized(
        self, 
        user_id: Optional[int] = None,
        liked_movies: Optional[List[int]] = None,
        genres: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """Gợi ý cá nhân hóa dựa trên danh sách phim đã thích (Profile Centroid)."""
        try:
            centroid = None
            if liked_movies:
                # Đã clean: Thay thế vòng lặp đơn bằng 1 lệnh mget duy nhất
                docs = await self._fetch_docs_by_ids(liked_movies, [ESFields.EMBEDDING])
                embeddings = [doc[ESFields.EMBEDDING] for doc in docs if ESFields.EMBEDDING in doc]
                centroid = self.embedding_provider.calculate_centroid(embeddings)
            
            if centroid:
                query = QueryTemplates.knn_search(
                    centroid, top_n * 2, top_n * 2, 
                    [ESFields.MOVIE_ID, ESFields.TITLE, ESFields.GENRES]
                )
                if genres:
                    query["query"] = {
                        "bool": {
                            "must": [query["query"]], 
                            "filter": [{"terms": {ESFields.GENRES: genres}}]
                        }
                    }
            else:
                # Fallback khi người dùng chưa thích phim nào: Trả về phim phổ biến nhất
                query = {
                    "size": top_n,
                    "query": {"match_all": {}},
                    "sort": [{"popularity": "desc"}]
                }
            
            results = await self.es.search(index=self.index, **query)
            return {
                "strategy": "PERSONALIZED_CBF",
                "recommendations": [self._format_hit(h) for h in results['hits']['hits']][:top_n]
            }
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {e}")
            raise

    async def search_by_text(self, text_query: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """Tìm kiếm kết hợp (Hybrid Search) giữa Text truyền thống và Vector."""
        try:
            vector = self.embedding_provider.encode(text_query)
            query = QueryTemplates.hybrid_search(
                text_query, vector, top_n, 
                [ESFields.MOVIE_ID, ESFields.TITLE, ESFields.GENRES, ESFields.PLOT]
            )
            results = await self.es.search(index=self.index, **query)
            return [self._format_hit(h) for h in results['hits']['hits']]
        except Exception as e:
            logger.error(f"Error searching by text '{text_query}': {e}")
            raise