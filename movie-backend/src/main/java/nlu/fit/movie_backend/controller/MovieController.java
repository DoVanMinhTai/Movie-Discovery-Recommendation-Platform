package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.model.Genre;
import nlu.fit.movie_backend.model.enumeration.CONTENTTYPE;
import nlu.fit.movie_backend.service.JWTService;
import nlu.fit.movie_backend.service.MovieService;
import nlu.fit.movie_backend.service.RateService;
import nlu.fit.movie_backend.viewmodel.movie.MediaContentGetVm;
import nlu.fit.movie_backend.viewmodel.movie.MovieHeroVm;
import nlu.fit.movie_backend.viewmodel.movie.MovieThumbnailVms;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/movie")
@AllArgsConstructor
@CrossOrigin(origins = "*")
public class MovieController {
    private final MovieService movieService;
    private final JWTService jWTService;
    private final RateService rateService;

    @GetMapping("/")
    public ResponseEntity<?> getAllMovies() {
        return ResponseEntity.ok(movieService.getAllMovies());
    }

    @GetMapping("/{movieId}")
    public ResponseEntity<MediaContentGetVm> getMediaContentById(@PathVariable Long movieId) {
        System.out.println(movieService.getMediaContentById(movieId));
        return ResponseEntity.ok(movieService.getMediaContentById(movieId));
    }

    @GetMapping("/movies/latest")
    public ResponseEntity<List<MovieThumbnailVms>> getLatestMovies(
            @RequestParam int page, @RequestParam int size
    ) {
        return ResponseEntity.ok(movieService.getLatestMovies(page, size));
    }

    @GetMapping("/movies/trending")
    public ResponseEntity<List<MovieThumbnailVms>> getMovieTrending(
            @RequestParam int limit
    ) {
        return ResponseEntity.ok(movieService.getMovieTrending(limit));
    }

    @GetMapping("/movies/top10")
    public ResponseEntity<List<MovieThumbnailVms>> getMovieTop10(
            @RequestParam CONTENTTYPE contenttype,
            @RequestParam int limit
    ) {
        return ResponseEntity.ok(movieService.getTop10(contenttype, limit));
    }

    @GetMapping("/movies/preferredGenres")
    public ResponseEntity<Map<String, List<MovieThumbnailVms>>> getMoviePreferredGenres(
            @RequestHeader("Authorization") String authHeader,
            @RequestParam(defaultValue = "10") int limit
    ) {
        String token = authHeader.substring(7);
        Long userId = jWTService.extractUserId(token);
        return ResponseEntity.ok(movieService.getMoviePreferredGenres(userId, limit));
    }

    @GetMapping("/movies/genres")
    public ResponseEntity<List<Genre>> getAllGenres() {
        return ResponseEntity.ok(movieService.getAllGenres());
    }

    @GetMapping("/movies/")
    public ResponseEntity<Page<MovieThumbnailVms>> getMoviesFilter(
            @RequestParam(name = "sortBy") String sortBy,
            @RequestParam(name = "genre", required = false) String genreId,
            @RequestParam(name = "page") int page,
            @RequestParam(name = "size") int size
    ) {
        return ResponseEntity.ok(movieService.filterMovies(sortBy, genreId, page, size));
    }

    @GetMapping("/movies/hero")
    public ResponseEntity<MovieHeroVm> getMovieHero(
    ) {
        return ResponseEntity.ok(movieService.getMovieHero());
    }


}
