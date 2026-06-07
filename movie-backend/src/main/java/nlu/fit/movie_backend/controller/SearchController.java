package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.constants.ApiEndpoints;
import nlu.fit.movie_backend.service.SearchService;
import nlu.fit.movie_backend.viewmodel.ApiResponse;
import nlu.fit.movie_backend.viewmodel.movie.MovieSearchGetVm;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@AllArgsConstructor
@CrossOrigin(origins = "${app.cors.allowed-origins}")
public class SearchController {
    private final SearchService searchService;

    @GetMapping(ApiEndpoints.Search.ALL)
    public ResponseEntity<ApiResponse<Page<MovieSearchGetVm>>> getAllMovieByTitle(
            @RequestParam("q") String query,
            @PageableDefault(size = 20) Pageable pageable) {
        return ResponseEntity.ok(ApiResponse.<Page<MovieSearchGetVm>>builder().result(searchService.getAllMovieByTitle(query, pageable)).build());
    }

    @GetMapping(ApiEndpoints.Search.SUGGESTION)
    public ResponseEntity<ApiResponse<List<MovieSearchGetVm>>> getMovieSuggestionByTitle(
            @RequestParam("q") String query) {
        return ResponseEntity.ok(ApiResponse.<List<MovieSearchGetVm>>builder().result(searchService.getMovieSuggestionByTitle(query)).build());
    }
}
