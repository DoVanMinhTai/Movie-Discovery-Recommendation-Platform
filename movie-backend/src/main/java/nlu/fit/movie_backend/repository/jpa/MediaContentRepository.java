package nlu.fit.movie_backend.repository.jpa;

import nlu.fit.movie_backend.model.MediaContent;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MediaContentRepository extends JpaRepository<MediaContent,Long> {
    Page<MediaContent> findByGenresId(Long genresId, Pageable pageable);

    List<MediaContent> findTop5ByOrderByIdDesc();
}
