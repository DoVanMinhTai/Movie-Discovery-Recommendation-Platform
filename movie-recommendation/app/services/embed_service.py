
import logging
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    _model: Optional[SentenceTransformer] = None
    _model_name: str = "all-MiniLM-L6-v2"
    
    @classmethod
    def get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            logger.info(f"Loading sentence-transformers model: {cls._model_name}")
            cls._model = SentenceTransformer(cls._model_name)
            logger.info("Model loaded successfully!")
        return cls._model
    
    @classmethod
    def encode(cls, text: str) -> List[float]:
        model = cls.get_model()
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    @classmethod
    def encode_batch(cls, texts: List[str]) -> List[List[float]]:
        model = cls.get_model()
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()
    
    @classmethod
    def calculate_centroid(cls, embeddings: List[List[float]]) -> Optional[List[float]]:    
        if not embeddings:
            return None
        
        embeddings_array = np.array(embeddings)
        centroid = np.mean(embeddings_array, axis=0)
        return centroid.tolist()
    
    @classmethod
    def is_loaded(cls) -> bool:
        return cls._model is not None
    
    @classmethod
    def unload(cls):
        if cls._model is not None:
            logger.info("Unloading sentence-transformers model")
            cls._model = None