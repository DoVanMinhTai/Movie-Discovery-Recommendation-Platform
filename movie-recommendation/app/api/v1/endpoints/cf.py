from fastapi import APIRouter, Depends, Request, HTTPException
from app.services.engines.cf_service import CollaborativeService
from app.api.dependencies import get_es_client
from elasticsearch import AsyncElasticsearch
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cf", tags=["Collaborative Filtering"])

def get_cf_service(es_client: AsyncElasticsearch = Depends(get_es_client)):
    return CollaborativeService(es_client)

@router.get("/user-recommendations/{user_id}")
async def get_user_recommendations(
    user_id: int,
    top_n: int = 10,
    service: CollaborativeService = Depends(get_cf_service)
):
    try:
        result = await service.get_user_recommendations(user_id, top_n)
        return result
    except Exception as e:
        logger.error(f"Error in CF Service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/item-similarity/{item_id}")
async def get_item_similarity(
    item_id: int,
    top_n: int = 10,
    service: CollaborativeService = Depends(get_cf_service)
):
    try:
        return await service.get_item_based_similar(item_id, top_n)
    except Exception as e:
        logger.error(f"Error in CF Similarity: {e}")
        raise HTTPException(status_code=500, detail=str(e))
