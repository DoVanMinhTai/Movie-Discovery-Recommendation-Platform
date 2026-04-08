package nlu.fit.movie_backend.repository.jpa;

import nlu.fit.movie_backend.model.Movie;
import org.springframework.data.domain.Limit;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.Collection;
import java.util.List;

@Repository
public interface MovieRepository extends JpaRepository<Movie, Long> {
    List<Movie> findAllByIsDeletedFalse(boolean isDeleted, Pageable pageable);

    List<Movie> findAllByIdIn(Collection<Long> ids, Limit limit);

    @Query("SELECT m FROM Movie m " +
            "WHERE m.isDeleted = false " +
            "ORDER BY m.popularity DESC")
    List<Movie> findGlobalTrending(Pageable pageable);

    Page<Movie> findAllByDtypeAndIsDeletedFalse(String dtype, Pageable pageable);

    Page<Movie> findByGenresIdAndIsDeletedFalse(Long genreId, Pageable pageable);
}
