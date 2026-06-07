package nlu.fit.movie_backend.repository.jpa;

import nlu.fit.movie_backend.model.WatchHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

@Repository
public interface WatchHistoryRepository extends JpaRepository<WatchHistory,Long> {

    boolean existsByUserIdAndMediaContentId(Long userId, Long mediaContentId);

    long countByWatchedAtBetween(LocalDateTime from, LocalDateTime to);

    @Query("SELECT CAST(w.watchedAt AS DATE), COUNT(w) FROM WatchHistory w WHERE w.watchedAt BETWEEN :from AND :to GROUP BY CAST(w.watchedAt AS DATE) ORDER BY CAST(w.watchedAt AS DATE)")
    List<Object[]> countDailyViewsBetween(@Param("from") LocalDateTime from, @Param("to") LocalDateTime to);
}
