from typing import List, Optional, Dict, Any
import numpy as np
from sqlalchemy.orm import Session
from opensearchpy import OpenSearch, AsyncOpenSearch
from sentence_transformers import SentenceTransformer
from app.models.media_content import Movie, Genre
from app.core.config import settings
from app.constants.query_template import QueryTemplates, SearchIndex
from app.services.embed_service import EmbeddingProvider
import logging

class ContentBasedService:
    def __init__(self, db: Session, es_client: OpenSearch, embedding_provider: EmbeddingProvider):
        self.db = db
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
            movie = self.db.query(Movie).filter(Movie.movie_id == movie_id).first()
            if not movie:
                raise ValueError(f"Movie {movie_id} not found")

            movie_doc = self._fetch_doc_by_id(movie_id, [ESFields.EMBEDDING])
            if not movie_doc:
                raise ValueError(f"Movie {movie_id} vector not found")

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
                "movie_title": movie.title,
                "recommendations": recommendations[:top_n]
            }
            
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
                
                if tags:
                    query["query"] = {"bool": {"must": [query["query"]], "filter": [{"terms": {ESFields.TAGS: tags}}]}}
            else:
                query = {
                "size": top_n,
                "query": {"terms": {ESFields.GENRES: genres or ["Action"]}},
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
            sort_field = CBFQueries.SORT_MAP.get(sort_by, CBFQueries.SORT_MAP[SortOption.POPULARITY])
            
            results = self.es_client.search(index=self.index_name, body=QueryTemplates.genre_filter_search([genre], top_n, sort_field, [ESFields.MOVIE_ID, ESFields.TITLE, ESFields.GENRES, sort_field]))
            
            recommendations = [self._format_hit(h) for h in results['hits']['hits']]
            
            return {
                "strategy": f"GENRE_{genre.upper()}_{sort_by.upper()}",
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error getting movies by genre '{genre}': {e}")
            raise
        
    async def get_trending(
        self, 
        time_window: str = "7d",
        top_n: int = 10
    ) -> Dict[str, Any]:

        try:
            from sqlalchemy import text
            
            days = {"1d": 1, "7d": 7, "30d": 30}[time_window]
            
            results = self.db.execute(
                text(CBFQueries.TRENDING_SQL), 
                {"days": days, "top_n": top_n}
            ).fetchall()
            
            if not results:
                return await self.get_by_genre("Action", top_n, "popularity")
            
            movie_ids = [r.movie_id for r in results]
            
            es_query = {
                "query": {
                    "terms": {"movie_id": movie_ids}
                },
                "_source": ["movie_id", "title", "genres"]
            }            
            es_results = self.es_client.search(index=self.index_name, body=es_query)
            
            movie_map = {
                hit['_source']['movie_id']: hit['_source']
                for hit in es_results['hits']['hits']
            }
            
            recommendations = [self._format_hit(h) for h in results['hits']['hits']]
            
            return {
                "strategy": f"TRENDING_{time_window.upper()}",
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error getting trending movies: {e}")
            raise