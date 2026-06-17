from enum import Enum

class SearchIndex(str, Enum):
    MOVIES = "movies_cbf"

class ESFields(str, Enum):
    MOVIE_ID = "movie_id"
    TITLE = "title"
    GENRES = "genres"
    EMBEDDING = "embedding"
    TAGS = "tags"
    PLOT = "plot"

class QueryTemplates:
        
    @staticmethod
    def knn_search(vector, k, size, source_fields):
        return {
            "size": size,
            "knn": {
                "field": ESFields.EMBEDDING,
                "query_vector": vector,
                "k": k,
                "num_candidates": 10 * k,
            },
            "source": source_fields
        }

    @staticmethod
    def hybrid_search(text_query, vector, size, source_fields):
        return {
        "size": size,
        "query": {
            "multi_match": {
                "query": text_query,
                "fields": ["title^2", "plot", "tags"],
                "boost": 0.3 
            }
        },
        "knn": {
            "field": "embedding",  
            "query_vector": vector,
            "k": size,
            "num_candidates": size * 10,
            "boost": 0.7
        },
        "source": source_fields
    }