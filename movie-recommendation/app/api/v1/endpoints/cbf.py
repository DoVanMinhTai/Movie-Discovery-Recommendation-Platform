import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from elasticsearch import NotFoundError

from app.services.engines.cbf_service import ContentBasedService, MovieNotFoundError
from app.api.dependencies import get_cbf_service


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cbf", tags=["Content-Based Filtering"])

@router.get("/similar/{movie_id}")
async def get_similar_movies(
    movie_id: int = Path(..., ge=1),
    top_n: int = Query(10, ge=1, le=50),
    service: ContentBasedService = Depends(get_cbf_service)
):
    try:
        return await service.find_similar_movies(movie_id, top_n)
    except (MovieNotFoundError, NotFoundError):
        raise HTTPException(status_code=404, detail="Movie not found")
    except Exception as e:
        logger.error(f"Error finding similar movies: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search")
async def search_movies_by_text(
    query: str = Query(..., min_length=3),
    top_n: int = Query(10, ge=1),
    service: ContentBasedService = Depends(get_cbf_service)
):
    try:
        return await service.search_by_text(query, top_n)
    except Exception as e:
        logger.error(f"Error searching movies: {e}")
        raise HTTPException(status_code=500, detail=str(e))