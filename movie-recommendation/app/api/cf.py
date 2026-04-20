from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.services.cf_service import CollaborativeService
from app.core.database import get_db
from app.schemas.base import RecommendationResponse, RecommendationItem

router = APIRouter(prefix="/cf", tags=["Collaborative Filtering"])

@router.get("/user-recommendations/{user_id}")
def get_user_recommendations(
    request: Request,
    user_id: int,
    top_n: int = 10,
    db: Session = Depends(get_db)
):
    collaborative_service = CollaborativeService(db, "")
    recommendations = collaborative_service.collaborative_filtering(request, user_id)
    
    return {
        "strategy": "COLLABORATIVE_FILTERING",
        "data": recommendations[:top_n]
    }


@router.get("/item-similarity/{item_id}")
def get_item_similarity(
    request: Request,
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Get similar items based on collaborative filtering similarities
    """
    # This would involve getting the item-factor representation from the model
    # and finding similar items based on factor similarity
    return {
        "item_id": item_id,
        "similar_items": [],
        "message": "Item similarity not yet implemented in this service"
    }