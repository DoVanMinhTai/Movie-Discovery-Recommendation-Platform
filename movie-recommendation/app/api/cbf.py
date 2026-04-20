from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from app.services.cbf_service import ContentBasedService
from app.core.database import get_db
from app.schemas.recommendation import (
    MovieSimilarResponse,
    PersonalizedRequest,
    PersonalizedResponse,
    MovieSearchResult,
    GenreRecommendationResponse,
    TrendingResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cbf", tags=["Content-Based Filtering"])

@router.get("/similar/{movie_id}", response_model=MovieSimilarResponse, summary="Get similar movies",
    description="Find similar movies using KNN vector search on Elasticsearch"
)
async def get_similar_movies(
    movie_id: int = Path(..., description="Target movie ID", ge=1),
    top_n: int = Query(10, description="Number of recommendations", ge=1, le=50),
    db: Session = Depends(get_db)
):
    try:
        service = ContentBasedService(db)
        result = await service.find_similar_movies(movie_id, top_n)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_similar_movies: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post(
    "/personalized",
    response_model=PersonalizedResponse,
    summary="Get personalized recommendations",
    description="Get recommendations based on user preferences and liked movies"
)
async def get_personalized_recommendations(
    request: PersonalizedRequest,
    db: Session = Depends(get_db)
):
    try:
        service = ContentBasedService(db)
        result = await service.get_personalized(
            user_id=request.user_id,
            liked_movies=request.liked_movies,
            genres=request.genres,
            tags=request.tags,
            top_n=request.top_n
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_personalized_recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get(
    "/search",
    response_model=List[MovieSearchResult],
    summary="Search movies by text",
    description="Search movies using hybrid search (BM25 + vector similarity)"
)
async def search_movies_by_text(
    query: str = Query(
        ..., 
        description="Search query (e.g., 'action movie with robots')",
        min_length=3,
        max_length=200
    ),
    top_n: int = Query(10, description="Number of results", ge=1, le=50),
    db: Session = Depends(get_db)
):
    try:
        service = ContentBasedService(db)
        results = await service.search_by_text(query, top_n)
        return results
    except Exception as e:
        logger.error(f"Error in search_movies_by_text: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get(
    "/by-genre/{genre}",
    response_model=GenreRecommendationResponse,
    summary="Get movies by genre",
    description="Get movies filtered by genre with sorting options"
)
async def get_movies_by_genre(
    genre: str = Path(
        ..., 
        description="Genre name (Action, Comedy, Drama, Horror, Romance, Sci-Fi, Thriller, etc.)"
    ),
    top_n: int = Query(10, description="Number of results", ge=1, le=50),
    sort_by: str = Query(
        "popularity",
        description="Sort order",
        pattern="^(popularity|rating|recent)$"
    ),
    db: Session = Depends(get_db)
):
    try:
        service = ContentBasedService(db)
        result = await service.get_by_genre(genre, top_n, sort_by)
        return result
    except Exception as e:
        logger.error(f"Error in get_movies_by_genre: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get(
    "/trending",
    response_model=TrendingResponse,
    summary="Get trending movies",
    description="Get trending movies based on recent ratings"
)
async def get_trending_movies(
    time_window: str = Query(
        "7d",
        description="Time window for trending calculation",
        pattern="^(1d|7d|30d)$"
    ),
    top_n: int = Query(10, description="Number of results", ge=1, le=50),
    db: Session = Depends(get_db)
):
    try:
        service = ContentBasedService(db)
        result = await service.get_trending(time_window, top_n)
        return result
    except Exception as e:
        logger.error(f"Error in get_trending_movies: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get(
    "/health",
    summary="Health check",
    description="Check if CBF service and Elasticsearch are healthy"
)
async def health_check(db: Session = Depends(get_db)):
    try:
        service = ContentBasedService(db)
        
        es_health = service.es_client.cluster.health()
        
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "elasticsearch": es_health['status'],
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
