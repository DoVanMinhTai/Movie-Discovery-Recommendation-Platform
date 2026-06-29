from typing import Optional
from fastapi import APIRouter, Depends, Request, Query, Path

from app.services.engines.hybrid_service import HybridService
from app.api.dependencies import get_hybrid_service

router = APIRouter(prefix="/hybrid", tags=["Hybrid Recommendations"])

@router.get("/recommendations/{user_id}")
async def get_hybrid_recommendations(
    request: Request,
    user_id: int = Path(..., ge=1),
    movie_id: Optional[int] = Query(None, ge=1),
    top_n: int = Query(10, ge=1, le=50),
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    recommendations = await hybrid_service.hybrid_recommendation(
        request, user_id, movie_id, top_n
    )
    
    return {
        "strategy": "HYBRID",
        "data": recommendations
    }


@router.post("/recommendations")
async def get_hybrid_recommendations_post(
    request: Request,
    user_id: int,
    movie_id: Optional[int] = None,
    top_n: int = 10,
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    recommendations = await hybrid_service.hybrid_recommendation(
        request, user_id, movie_id, top_n
    )
    
    return {
        "strategy": "HYBRID",
        "data": recommendations
    }