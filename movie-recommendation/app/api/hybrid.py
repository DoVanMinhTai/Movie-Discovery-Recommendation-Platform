from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.services.hybrid_service import HybridService
from app.schemas.base import RecommendationResponse
from app.services.cbf_service import ContentBasedService
from app.services.cf_service import CollaborativeService
from app.services.es_service import get_es_client, EsService # Added EsService
from opensearchpy import OpenSearch
from app.services.embed_service import EmbeddingProvider

router = APIRouter(prefix="/hybrid", tags=["Hybrid Recommendations"])

def get_embedding_provider() -> EmbeddingProvider:
    return EmbeddingProvider()

@router.get("/recommendations/{user_id}")
async def get_hybrid_recommendations(
    request: Request,
    user_id: int,
    movie_id: int = None,
    top_n: int = 10,
):
    es_client = get_es_client()
    es_service = EsService(es_client) 
    cbf = ContentBasedService(es_client, get_embedding_provider())
    cf = CollaborativeService(es_client)
    
    hybrid_service = HybridService(cbf, cf, es_service)
    
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
    movie_id: int = None,
    top_n: int = 10,
):
    es_client = get_es_client()
    es_service = EsService(es_client)
    cbf = ContentBasedService(es_client, get_embedding_provider())
    cf = CollaborativeService(es_client)
    
    hybrid_service = HybridService(cbf, cf, es_service)
    
    recommendations = await hybrid_service.hybrid_recommendation(
        request, user_id, movie_id, top_n
    )
    
    return {
        "strategy": "HYBRID",
        "data": recommendations
    }
