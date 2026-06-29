from fastapi import APIRouter
from app.api.v1.endpoints.cbf import router as cbf_router
from app.api.v1.endpoints.cf import router as cf_router
from app.api.v1.endpoints.hybrid import router as hybrid_router

api_router = APIRouter()

api_router.include_router(cbf_router, tags=["Content-Based Filtering"])
api_router.include_router(cf_router, tags=["Collaborative Filtering"])
api_router.include_router(hybrid_router, tags=["Hybrid Recommendations"])
