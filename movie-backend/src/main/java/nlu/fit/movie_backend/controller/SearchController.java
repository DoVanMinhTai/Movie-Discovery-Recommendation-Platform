package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.service.SearchService;
import nlu.fit.movie_backend.viewmodel.movie.MovieSearchGetVm;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/search")
@AllArgsConstructor
@CrossOrigin(origins = "*")
public class SearchController {
    private final SearchService searchService;

    @GetMapping("/all")
    public ResponseEntity<Page<MovieSearchGetVm>> getAllMovieByTitle(
            @RequestParam("q") String query,
            @PageableDefault(size = 20) Pageable pageable) {
        return ResponseEntity.ok(searchService.getAllMovieByTitle(query, pageable));
    }

    @GetMapping("/suggest")
    public ResponseEntity<List<MovieSearchGetVm>> getMovieSuggestionByTitle(
            @RequestParam("q") String query) {
        return ResponseEntity.ok(searchService.getMovieSuggestionByTitle(query));
    }
}
