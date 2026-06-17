from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title="Media Recommendation System",
    description="A FastAPI application for movie recommendations using various algorithms",
    version="1.0.0")

app.include_router(api_router, prefix="/api/v1")

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