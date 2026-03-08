import os, glob, joblib
from config.config import Settings

def load_model_latest():
    settings = Settings()
    search_Path = os.path.join(settings.model_base,"*.pkl")
    list_of_files = glob.glob(search_Path)
    
    if not list_of_files:
        print(f"WARNING: No model files found matching pattern: {search_Path}")
        return None
    
    latest_file = max(list_of_files, key=os.path.getctime)
    return joblib.load(latest_file)


def load_content_model():
    settings = Settings()
    matrix_path = os.path.join(settings.model_base, "tfidf_matrix.pkl")
    movies_path = os.path.join(settings.model_base, "movies_merged.pkl")
    if not os.path.exists(matrix_path) or not os.path.exists(movies_path):
        print(f"WARNING: Content based model files not found at: {matrix_path} or {movies_path}")
        return None
    tfidf_matrix = joblib.load(matrix_path)
    movies_merged = joblib.load(movies_path)
    return {"matrix": tfidf_matrix, "movies": movies_merged}

def load_collaborative_model():
    settings = Settings()
    model_path = os.path.join(settings.model_base, "svd_model.pkl")
    if not os.path.exists(model_path):
        print(f"WARNING: SVD model not found at: {model_path}")
        return None
    return joblib.load(model_path)