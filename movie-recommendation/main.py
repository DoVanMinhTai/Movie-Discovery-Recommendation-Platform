from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from app.core.database import Base, engine
from app.api import cbf, cf, hybrid
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Media Recommendation System",
    description="A FastAPI application for movie recommendations using various algorithms",
    version="1.0.0")

app.include_router(cbf.router, prefix="/api/v1", tags=["Content-Based Filtering"])
app.include_router(cf.router, prefix="/api/v1", tags=["Collaborative Filtering"])
app.include_router(hybrid.router, prefix="/api/v1", tags=["Hybrid Recommendations"])

@app.get("/")
def root():
    return {"message": "Welcome to Media Recommendation System API"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )