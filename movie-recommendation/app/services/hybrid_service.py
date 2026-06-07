from fastapi import Request
from sqlalchemy.orm import Session
from app.schemas.base import RecommendationItem
import numpy as np
import logging

logger = logging.getLogger("HybridService")

class HybridService:
    def __init__(self, cbf_service=None, cf_service=None, es_service=None):
        self.cbf_service = cbf_service
        self.cf_service = cf_service
        self.es_service = es_service 

    async def hybrid_recommendation(self, request: Request, user_id: int, movie_id: int = None, top_n: int = 10):
        cbf_data = []
        cf_recs = []
        
        if self.cbf_service and movie_id:
            try:
                cbf_result = await self.cbf_service.find_similar_movies(movie_id, top_n)
                cbf_data = cbf_result.get('recommendations', [])
            except Exception as e:
                logger.error(f"CBF Error: {e}")

        if self.cf_service and user_id:
            try:
                cf_recs = await self.cf_service.get_user_recommendations(user_id)
            except Exception as e:
                logger.error(f"CF Error: {e}")

        combined_recs = await self._combine_recommendations(cbf_data, cf_recs)
        final_top_ids = combined_recs[:top_n]

        if self.es_service:
            enriched_data = []
            for item in final_top_ids:
                metadata = await self.es_service.get_movie_by_id(item.movie_id)
                if metadata:
                    item.title = metadata.get('title')
                    item.poster_path = metadata.get('poster_path')
                    item.slug = metadata.get('slug')
                enriched_data.append(item)
            return enriched_data
        
        return final_top_ids

    async def _combine_recommendations(self, cbf_recs, cf_recs, cbf_weight=0.4, cf_weight=0.6):
        combined_scores = {}
        
        for rec in cbf_recs:
            m_id = rec.get('movieId') or rec.get('movie_id')
            if m_id:
                score = rec.get('score', 0.0)
                combined_scores[m_id] = combined_scores.get(m_id, 0.0) + cbf_weight * score
        
        for rec in cf_recs:
            m_id = getattr(rec, 'movie_id', None)
            if m_id:
                score = getattr(rec, 'score', 0.0)
                combined_scores[m_id] = combined_scores.get(m_id, 0.0) + cf_weight * score
        
        result = []
        sorted_items = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        for m_id, score in sorted_items:
            result.append(RecommendationItem(movie_id=int(m_id), score=float(score)))
        
        return result
