from fastapi import Request
from sqlalchemy.orm import Session
from app.schemas.base import RecommendationItem
import numpy as np

class HybridService:
    def __init__(self, db: Session, model_dir: str):
        self.db = db
        self.model_dir = model_dir

    def hybrid_recommendation(self, request: Request, user_id: int, movie_id: int = None, top_n: int = 10):
        cbf_service = self._get_cbf_service(request)
        cf_service = self._get_cf_service(request)
        
        cbf_recs = []
        cf_recs = []
        
        if cbf_service:
            # Get content-based recommendations
            if movie_id:
                cbf_recs = cbf_service.find_similar_movies(request, movie_id, top_n)
        
        if cf_service and user_id:
            # Get collaborative filtering recommendations
            cf_recs = cf_service.collaborative_filtering(request, user_id)
        
        # Combine and weight the recommendations
        combined_recs = self._combine_recommendations(cbf_recs, cf_recs)
        
        return combined_recs[:top_n]

    def _get_cbf_service(self, request: Request):
        """Get content-based filtering service instance"""
        from .cbf_service import ContentBasedService
        # Return a service instance with a mock database session
        # In a real implementation, you'd have proper dependency injection
        return None  # Placeholder

    def _get_cf_service(self, request: Request):
        """Get collaborative filtering service instance"""
        from .cf_service import CollaborativeService
        # Return a service instance with a mock database session
        # In a real implementation, you'd have proper dependency injection
        return None  # Placeholder

    def _combine_recommendations(self, cbf_recs, cf_recs, cbf_weight=0.3, cf_weight=0.7):
        """
        Combine content-based and collaborative filtering recommendations
        """
        # This is a simplified combination method
        # In practice, you might use more sophisticated techniques
        combined_scores = {}
        
        # Process content-based recommendations
        for rec in cbf_recs:
            movie_id = rec.get('movieId', rec.get('movie_id', None))
            if movie_id:
                score = rec.get('score', 0.0)
                combined_scores[movie_id] = combined_scores.get(movie_id, 0.0) + cbf_weight * score
        
        # Process collaborative filtering recommendations
        for rec in cf_recs:
            movie_id = getattr(rec, 'movie_id', None)
            if movie_id:
                score = getattr(rec, 'score', 0.0)
                combined_scores[movie_id] = combined_scores.get(movie_id, 0.0) + cf_weight * score
        
        # Convert to RecommendationItem format
        result = []
        for movie_id, score in sorted(combined_scores.items(), key=lambda x: x[1], reverse=True):
            result.append(RecommendationItem(movie_id=movie_id, score=score))
        
        return result