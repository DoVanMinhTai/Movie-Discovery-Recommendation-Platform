from typing import List, Any
from app.core.constants import ESFields


def knn_search(vector: List[float], k: int, size: int, source_fields: List[str]) -> dict:
    return {
        "size": size,
        "query": {"knn": {ESFields.EMBEDDING: {"vector": vector, "k": k}}},
        "_source": source_fields
    }


def hybrid_search(text_query: str, vector: List[float], size: int, source_fields: List[str]) -> dict:
    return {
        "size": size,
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": text_query,
                            "fields": ["title^2", "plot", "tags"],
                            "boost": 0.3
                        }
                    },
                    {
                        "knn": {
                            ESFields.EMBEDDING: {
                                "vector": vector,
                                "k": size,
                                "boost": 0.7
                            }
                        }
                    }
                ]
            }
        },
        "_source": source_fields
    }


def popularity_search(size: int, source_fields: List[str]) -> dict:
    return {
        "size": size,
        "query": {"match_all": {}},
        "sort": [{"popularity": "desc"}],
        "_source": source_fields
    }


def genre_filter_search(genres: List[str], size: int, sort_field: str, source_fields: List[str]) -> dict:
    return {
        "size": size,
        "query": {
            "bool": {
                "filter": {"terms": {ESFields.GENRES: genres}}
            }
        },
        "sort": [sort_field],
        "_source": source_fields
    }
