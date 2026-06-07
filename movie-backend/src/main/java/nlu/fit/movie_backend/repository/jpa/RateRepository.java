package nlu.fit.movie_backend.repository.jpa;

import nlu.fit.movie_backend.model.Rating;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.Optional;

@Repository
public interface RateRepository extends JpaRepository<Rating, Long> {
    Optional<Rating> findByUserIdAndMediaContentId(Long userId, Long mediaContentId);

    long countByCreatedAtBetween(LocalDateTime from, LocalDateTime to);
}
