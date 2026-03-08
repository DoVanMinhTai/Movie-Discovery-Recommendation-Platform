from typing import List
from fastapi import APIRouter, Depends, Request
from services.content_based_service import ContentBasedService as content_based_service
from services.collaborative_service import CollaborativeService as collaborative_service
from common.database import get_db
from sqlalchemy.orm import Session
from model.model_registry import RecommendationItem, RecommendationResponse, UserContext
from model.media_content import Movie, Genre
from config.config import Settings

class RecommendationController:
    def __init__(self, db: Session):
        self.db = db
        # self.model_dir = Path(__file__).resolve().parent.parent.parent / "model-store"
        self.content_based_service = content_based_service(db, str(Settings.model_base))
        self.collaborative_service = collaborative_service(db, str(Settings.model_base))

router = APIRouter(prefix= "/recommendation", tags=["Recommendation"])

@router.get("/getMovieSimilar/{movie_id}")
def get_similar_movies(request: Request, movie_id: int):
    recommendationService = RecommendationController(db=Depends(get_db))
    return recommendationService.content_based_service.find_similar_movies(request, movie_id=movie_id, top_n=10)

@router.post("/personalized" , response_model= RecommendationResponse)
def get_user_feed( request: Request, ctx : UserContext, db: Session = Depends(get_db)):
    recommendationService = RecommendationController(db=db)
    if ctx.selected_Genres:
        return RecommendationResponse(
                strategy="GENRE",
                data=query_db_by_genre(ctx.selected_Genres, db, 10))
    
    if not ctx.is_new_user and ctx.user_Id:
        return [
            RecommendationResponse(
                strategy="COLLABORATIVE_FILTERING",
                data=recommendationService.collaborative_service.collaborative_filtering(request, ctx.user_Id))
        ]
    return [
        RecommendationResponse(
            strategy="POPULAR",
            data=get_popular_movies(db)
        )
    ]

def query_db_by_genre(genres: List[str], db: Session = Depends(get_db), limit: int = 10):
    movies = db.query(Movie).join(Movie.genres).filter(
        Genre.name.in_(genres)
    ).distinct().limit(limit).all()
    
    return [
        RecommendationItem(movie_id=m.movie_id, score=1.0) for m in movies
    ]

def get_popular_movies(db: Session):
    movies = db.query(Movie).order_by(Movie.popularity.desc()).limit(10).all()
    
    return [
        RecommendationItem(movie_id=m.movie_id, score=m.popularity) for m in movies
    ]