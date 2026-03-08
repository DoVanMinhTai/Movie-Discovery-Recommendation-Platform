from fastapi import Request
from sqlalchemy.orm import Session
from model.model_registry import RecommendationItem

class CollaborativeService:
    def __init__(self, db: Session, model_dir: str):
        self.db = db
        self.model_dir = model_dir

    def collaborative_filtering(self, request: Request, user_id: int):
        model = request.app.state.ml_models.get("collaborative_filtering")
        
        if not model:
            return []
        
        all_movie_ids = range(1, 1000) 
        
        recommendations = []
        
        for movie_id in all_movie_ids:
            predicted_rating = model.predict(user_id, movie_id).est
            recommendations.append(RecommendationItem(movie_id=movie_id, score=predicted_rating))
        
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:10]