package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.constants.ApiEndpoints;
import nlu.fit.movie_backend.model.Genre;
import nlu.fit.movie_backend.service.GenreService;
import nlu.fit.movie_backend.viewmodel.ApiResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@AllArgsConstructor
@CrossOrigin(origins = "${app.cors.allowed-origins}")
public class GenreController {
    private final GenreService genreService;

    @GetMapping(ApiEndpoints.Category.ALL)
    public ResponseEntity<ApiResponse<List<Genre>>> getAllGenres() {
        return ResponseEntity.ok(ApiResponse.<List<Genre>>builder().result(genreService.getAllGenres()).build());
    }
}
