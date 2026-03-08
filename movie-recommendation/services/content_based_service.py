from fastapi import Request
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sqlalchemy.orm import Session
from model.model_registry import Model_Registry

class ContentBasedService:
    def __init__(self, db: Session, model_dir: str):
        self.db = db
        self.model_dir = model_dir
        
    def find_similar_movies(self, request: Request, movie_id: int, top_n: int = 10):
        models = request.app.state.ml_models.get("content_based_filtering")
        if not models:
            return {"error": "Content-based filtering model not loaded."}
        cosine_sim = models["matrix"]
        df = models["movies"]  
        mask = df["movieId"] == movie_id
        matching_indices = df.index[mask]

        if len(matching_indices) == 0:
            return {"error": f"Movie ID {movie_id} not found in the dataset. Available range: {df['movieId'].min()} to {df['movieId'].max()}"}

        idx = matching_indices[0]
        
        if hasattr(cosine_sim, "toarray"):
            row_scores = cosine_sim[idx].toarray().flatten()
        elif hasattr(cosine_sim[idx], "toarray"):
            row_scores = cosine_sim[idx].toarray().flatten()
        else:
            row_scores = cosine_sim[idx]
        
        sim_scores = list(enumerate(row_scores))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n+1]
        movie_indices = [i[0] for i in sim_scores]
        similar_movies = df.iloc[movie_indices][["movieId", "title"]]
        return similar_movies.to_dict(orient="records")
   