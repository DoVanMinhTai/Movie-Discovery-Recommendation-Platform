package nlu.fit.movie_backend.repository.jpa;

import nlu.fit.movie_backend.model.TrainingJobsLogs;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TrainingJobRepository extends JpaRepository<TrainingJobsLogs, String> {
    List<TrainingJobsLogs> findTop10ByOrderByCreatedAtDesc();
}
