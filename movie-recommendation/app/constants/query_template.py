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
            "query": {"knn": {ESFields.EMBEDDING: {"vector": vector, "k": k}}},
            "_source": source_fields
        }

    @staticmethod
    def hybrid_search(text_query, vector, size, source_fields):
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
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                    "params": {"query_vector": vector}
                                },
                                "boost": 0.7
                            }
                        }
                    ]
                }
            },
            "_source": source_fields
        }
    
    def popularity_search(size, source_fields):
        return {
            "size": size,
            "query": {"match_all": {}},
            "sort": [{"popularity": "desc"}],
            "_source": source_fields
            }
    
    def genre_filter_search(genres, size, sort_field, source_fields):
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