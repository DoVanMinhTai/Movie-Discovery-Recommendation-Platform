package nlu.fit.movie_backend.repository.jpa;

import nlu.fit.movie_backend.model.WatchHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface WatchHistoryRepository extends JpaRepository<WatchHistory,Long> {

    boolean existsByUserIdAndMediaContentId(Long userId, Long mediaContentId);
}
