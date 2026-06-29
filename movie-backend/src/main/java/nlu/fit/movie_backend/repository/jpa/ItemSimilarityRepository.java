package nlu.fit.movie_backend.repository.jpa;

import nlu.fit.movie_backend.model.MediaContent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ItemSimilarityRepository extends JpaRepository<MediaContent, Long> {

    @Query(value = """
        SELECT m.media_content_id, m.title, m.backdrop_path, m.poster_path, m.overview, m.release_date, m.popularity, m.tmdb_vote, m.vote_count, m.original_language, m.original_title, m.dtype, m."cast", m.director, m.movie_lens_id, m.tmdb_id, m.is_deleted,
               mov.runtime, mov.trailer_key, mov.video_url,
               ser.status
        FROM mediacontent m
        LEFT JOIN movies mov ON m.media_content_id = mov.media_content_id
        LEFT JOIN series ser ON m.media_content_id = ser.media_content_id
        JOIN item_similarity s ON m.media_content_id = s.movie_id_2
        WHERE s.movie_id_1 = :movieId
        ORDER BY s.similarity DESC
        LIMIT :limit
    """, nativeQuery = true)
    List<MediaContent> findSimilarMoviesPrecomputed(@Param("movieId") Long movieId, @Param("limit") int limit);

    @Query(value = """
        WITH user_rated AS (
            SELECT mediacontent_id, score 
            FROM ratings 
            WHERE user_id = :userId AND score >= 3
        )
        SELECT m.media_content_id, m.title, m.backdrop_path, m.poster_path, m.overview, m.release_date, m.popularity, m.tmdb_vote, m.vote_count, m.original_language, m.original_title, m.dtype, m."cast", m.director, m.movie_lens_id, m.tmdb_id, m.is_deleted,
               mov.runtime, mov.trailer_key, mov.video_url,
               ser.status
        FROM mediacontent m
        LEFT JOIN movies mov ON m.media_content_id = mov.media_content_id
        LEFT JOIN series ser ON m.media_content_id = ser.media_content_id
        JOIN (
            SELECT s.movie_id_2 as target_id, AVG(s.similarity * ur.score) as weighted_score
            FROM user_rated ur
            JOIN item_similarity s ON ur.mediacontent_id = s.movie_id_1
            WHERE NOT EXISTS (
                SELECT 1 FROM ratings r 
                WHERE r.user_id = :userId AND r.mediacontent_id = s.movie_id_2
            )
            GROUP BY s.movie_id_2
        ) rec ON m.media_content_id = rec.target_id
        ORDER BY rec.weighted_score DESC
        LIMIT :limit
    """, nativeQuery = true)
    List<MediaContent> findPersonalizedCFPrecomputed(@Param("userId") Long userId, @Param("limit") int limit);
}
