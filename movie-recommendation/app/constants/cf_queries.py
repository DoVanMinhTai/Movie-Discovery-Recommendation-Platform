from enum import Enum

class CFStrategy(str, Enum):
    COLLABORATIVE = "COLLABORATIVE_FILTERING"
    ITEM_BASED = "ITEM_BASED_CF"
    COLD_START = "COLD_START_POPULAR"

class CollaborativeQueries:
    
    USER_RECOMMENDATIONS = """
        WITH user_rated_movies AS (
            SELECT movie_id, rating FROM ratings
            WHERE user_id = :user_id AND rating >= 4.0
        ),
        similar_movies AS (
            SELECT 
                s.movie_id_2 as movie_id,
                AVG(s.similarity * urm.rating) as weighted_score
            FROM user_rated_movies urm
            JOIN item_similarity s ON urm.movie_id = s.movie_id_1
            WHERE s.method = 'item_cf'
              AND s.movie_id_2 NOT IN (SELECT movie_id FROM user_rated_movies)
            GROUP BY s.movie_id_2
        )
        SELECT m.movie_id, m.title, m.genres, sm.weighted_score as score
        FROM similar_movies sm
        JOIN movies m ON sm.movie_id = m.movie_id
        ORDER BY sm.weighted_score DESC LIMIT :top_n
    """

    ITEM_SIMILAR = """
        SELECT m.movie_id, m.title, m.genres, s.similarity as score
        FROM item_similarity s
        JOIN movies m ON s.movie_id_2 = m.movie_id
        WHERE s.movie_id_1 = :movie_id AND s.method = 'item_cf'
        ORDER BY s.similarity DESC LIMIT :top_n
    """

    SIMILAR_USERS = """
        SELECT user_id_2 as user_id, similarity as score
        FROM user_similarity
        WHERE user_id_1 = :user_id
        ORDER BY similarity DESC LIMIT :top_n
    """

    COLD_START_POPULAR = """
        SELECT m.movie_id, m.title, m.genres, AVG(r.rating) as score
        FROM movies m
        JOIN ratings r ON m.movie_id = r.movie_id
        GROUP BY m.movie_id, m.title, m.genres
        HAVING COUNT(r.rating_id) >= 50
        ORDER BY score DESC, COUNT(r.rating_id) DESC LIMIT :top_n
    """