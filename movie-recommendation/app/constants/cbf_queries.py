from enum import Enum
from datetime import timedelta

class SortOption(str, Enum):
    POPULARITY = "popularity"
    RATING = "rating"
    RECENT = "recent"

class TimeWindow(str, Enum):
    DAY = "1d"
    WEEK = "7d"
    MONTH = "30d"

class CBFQueries:
    SORT_MAP = {
        SortOption.POPULARITY: {"popularity": {"order": "desc"}},
        SortOption.RATING: {"avg_rating": {"order": "desc"}},
        SortOption.RECENT: {"release_date": {"order": "desc"}}
    }

    TRENDING_SQL = """
        SELECT 
            movie_id,
            COUNT(*) as rating_count,
            AVG(rating) as avg_rating,
            (COUNT(*) * AVG(rating)) as trending_score
        FROM ratings
        WHERE created_at >= CURRENT_DATE - (:days * INTERVAL '1 day')
        GROUP BY movie_id
        HAVING COUNT(*) >= 5
        ORDER BY trending_score DESC
        LIMIT :top_n
    """