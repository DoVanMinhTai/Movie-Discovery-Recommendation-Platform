from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.services.hybrid_service import HybridService
from app.core.database import get_db
from app.schemas.base import RecommendationResponse

router = APIRouter(prefix="/hybrid", tags=["Hybrid Recommendations"])

@router.get("/recommendations/{user_id}")
def get_hybrid_recommendations(
    request: Request,
    user_id: int,
    movie_id: int = None,
    top_n: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recommendations using a hybrid approach combining content-based 
    and collaborative filtering
    """
    hybrid_service = HybridService(db, "")
    recommendations = hybrid_service.hybrid_recommendation(
        request, user_id, movie_id, top_n
    )
    
    return {
        "strategy": "HYBRID",
        "data": recommendations
    }


@router.post("/recommendations")
def get_hybrid_recommendations_post(
    request: Request,
    user_id: int,
    movie_id: int = None,
    top_n: int = 10,
    db: Session = Depends(get_db)
):
    hybrid_service = HybridService(db, "")
    recommendations = hybrid_service.hybrid_recommendation(
        request, user_id, movie_id, top_n
    )
    
    return {
        "strategy": "HYBRID",
        "data": recommendations
    }