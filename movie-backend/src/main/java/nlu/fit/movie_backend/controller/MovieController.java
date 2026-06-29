package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.constants.ApiEndpoints;
import nlu.fit.movie_backend.model.enumeration.CONTENTTYPE;
import nlu.fit.movie_backend.service.JWTService;
import nlu.fit.movie_backend.service.MovieService;
import nlu.fit.movie_backend.viewmodel.ApiResponse;
import nlu.fit.movie_backend.viewmodel.movie.MediaContentGetVm;
import nlu.fit.movie_backend.viewmodel.movie.MovieHeroGetVm;
import nlu.fit.movie_backend.viewmodel.movie.MovieThumbnailGetVm;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@AllArgsConstructor
@CrossOrigin(origins = "${app.cors.allowed-origins}")
public class MovieController {
    private final MovieService movieService;
    private final JWTService jWTService;

    @GetMapping(ApiEndpoints.Movie.MOVIES)
    public ResponseEntity<ApiResponse<List<MovieThumbnailGetVm>>> getAllMovies() {
        return ResponseEntity.ok(ApiResponse.<List<MovieThumbnailGetVm>>builder().result(movieService.getAllMovies()).build());
    }

    @GetMapping(ApiEndpoints.Movie.LATEST_MOVIES)
    public ResponseEntity<ApiResponse<List<MovieThumbnailGetVm>>> getLatestMovies(
            @RequestParam int page, @RequestParam int size
    ) {
        return ResponseEntity.ok(ApiResponse.<List<MovieThumbnailGetVm>>builder().result(movieService.getLatestMovies(page, size)).build());
    }

    @GetMapping(ApiEndpoints.Movie.TRENDING)
    public ResponseEntity<ApiResponse<List<MovieThumbnailGetVm>>> getTrendingMovies(
            @RequestParam int limit
    ) {
        return ResponseEntity.ok(ApiResponse.<List<MovieThumbnailGetVm>>builder().result(movieService.getTrendingMovies(limit)).build());
    }

    @GetMapping(ApiEndpoints.Movie.TOP10)
    public ResponseEntity<ApiResponse<List<MovieThumbnailGetVm>>> getMovieTop10(
            @RequestParam CONTENTTYPE contenttype,
            @RequestParam int limit
    ) {
        return ResponseEntity.ok(ApiResponse.<List<MovieThumbnailGetVm>>builder().result(movieService.getTop10(contenttype, limit)).build());
    }

    @GetMapping(ApiEndpoints.Movie.MOVIE_GENRES)
    public ResponseEntity<ApiResponse<Map<String, List<MovieThumbnailGetVm>>>> getMoviePreferredGenres(
            @RequestHeader("Authorization") String authHeader,
            @RequestParam(defaultValue = "10") int limit
    ) {
        String token = authHeader.substring(7);
        Long userId = jWTService.extractUserId(token);
        return ResponseEntity.ok(ApiResponse.<Map<String, List<MovieThumbnailGetVm>>>builder().result(movieService.getMoviePreferredGenres(userId, limit)).build());
    }

    @GetMapping(ApiEndpoints.Movie.FILTER)
    public ResponseEntity<ApiResponse<Page<MovieThumbnailGetVm>>> getMoviesFilter(
            @RequestParam(name = "sortBy") String sortBy,
            @RequestParam(name = "genre", required = false) String genreId,
            @RequestParam(name = "dtype", required = false) String dtype,
            @RequestParam(name = "page") int page,
            @RequestParam(name = "size") int size
    ) {
        return ResponseEntity.ok(ApiResponse.<Page<MovieThumbnailGetVm>>builder().result(movieService.filterMovies(sortBy, genreId, dtype, page, size)).build());
    }

    @GetMapping(ApiEndpoints.Movie.HERO)
    public ResponseEntity<ApiResponse<MovieHeroGetVm>> getMovieHero() {
        return ResponseEntity.ok(ApiResponse.<MovieHeroGetVm>builder().result(movieService.getMovieHero()).build());
    }

}
