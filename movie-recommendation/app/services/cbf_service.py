from typing import List, Optional, Dict, Any
import numpy as np
from opensearchpy import OpenSearch
from app.constants.query_template import QueryTemplates, SearchIndex, ESFields
from app.services.embed_service import EmbeddingProvider
import logging

logger = logging.getLogger(__name__)

class ContentBasedService:
    def __init__(self, es_client: OpenSearch, embedding_provider: EmbeddingProvider):
        self.es = es_client
        self.embedding_provider = embedding_provider
        self.index = SearchIndex.MOVIES
    
    def _fetch_doc_by_id(self, doc_id: int, fields: List[str]) -> Dict[str, Any]:
        try:
            res = self.es.get(index=self.index, id=str(doc_id), _source=fields)
            return res['_source']
        except Exception as e:
            logger.error(f"Doc {doc_id} not found in ES: {e}")
            return {}

    def _format_hit(self, hit: Dict) -> Dict:
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
    
        try:
            movie_doc = self._fetch_doc_by_id(movie_id, [ESFields.TITLE, ESFields.EMBEDDING])
            if not movie_doc:
                raise ValueError(f"Movie {movie_id} not found in Elasticsearch")

            query = QueryTemplates.knn_search(
                vector=movie_doc[ESFields.EMBEDDING],
                k=top_n + 1,
                size=top_n + 1,
                source_fields=[ESFields.MOVIE_ID, ESFields.TITLE, ESFields.GENRES]
            )
            
            results = self.es.search(index=self.index, body=query)
            
            recommendations = [
                self._format_hit(h) for h in results['hits']['hits'] 
                if h['_source'][ESFields.MOVIE_ID] != movie_id
            ]

            return {
                "movie_id": movie_id,
                "movie_title": movie_doc.get(ESFields.TITLE, "Unknown"),
                "recommendations": recommendations[:top_n]
            }
            
        except Exception as e:
            logger.error(f"Error finding similar movies for {movie_id} via ES: {e}")
            raise

    async def get_personalized(
        self, 
        user_id: Optional[int] = None,
        liked_movies: Optional[List[int]] = None,
        genres: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        top_n: int = 10
    ) -> Dict[str, Any]:

        try:
            centroid = None
            embeddings = []
            if liked_movies:
                for mid in liked_movies:
                    doc = self._fetch_doc_by_id(mid, [ESFields.EMBEDDING])
                    if doc: embeddings.append(doc[ESFields.EMBEDDING])
            
            centroid = self.embedding_provider.calculate_centroid(embeddings)
            
            if centroid:
                query = QueryTemplates.knn_search(centroid, top_n * 2, top_n * 2, [ESFields.MOVIE_ID, ESFields.TITLE, ESFields.GENRES])
                if genres:
                    query["query"] = {"bool": {"must": [query["query"]], "filter": [{"terms": {ESFields.GENRES: genres}}]}}
            else:
                query = {
                    "size": top_n,
                    "query": {"match_all": {}},
                    "sort": [{"popularity": "desc"}]
                }
            
            results = self.es.search(index=self.index, body=query)
            return {
                "strategy": "PERSONALIZED_CBF",
                "recommendations": [self._format_hit(h) for h in results['hits']['hits']][:top_n]
            }
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {e}")
            raise

    async def search_by_text(self, text_query: str, top_n: int = 10) -> List[Dict[str, Any]]:
        try:
            vector = self.embedding_provider.encode(text_query)
            query = QueryTemplates.hybrid_search(
                text_query, vector, top_n, 
                [ESFields.MOVIE_ID, ESFields.TITLE, ESFields.GENRES, ESFields.PLOT]
            )
            results = self.es.search(index=self.index, body=query)
            return [self._format_hit(h) for h in results['hits']['hits']]
        except Exception as e:
            logger.error(f"Error searching by text '{text_query}': {e}")
            raise

    async def get_by_genre(
        self, 
        genre: str, 
        top_n: int = 10,
        sort_by: str = "popularity"
    ) -> Dict[str, Any]:
        try:
            from app.constants.cbf_queries import CBFQueries, SortOption
            sort_field = CBFQueries.SORT_MAP.get(sort_by, CBFQueries.SORT_MAP[SortOption.POPULARITY])
            results = self.es.search(index=self.index, body=QueryTemplates.genre_filter_search([genre], top_n, sort_field, [ESFields.MOVIE_ID, ESFields.TITLE, ESFields.GENRES, sort_field]))
            return {
                "strategy": f"GENRE_{genre.upper()}_{sort_by.upper()}",
                "recommendations": [self._format_hit(h) for h in results['hits']['hits']]
            }
        except Exception as e:
            logger.error(f"Error getting movies by genre '{genre}': {e}")
            raise