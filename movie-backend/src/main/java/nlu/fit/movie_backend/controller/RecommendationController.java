package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.service.RecommendationService;
import nlu.fit.movie_backend.viewmodel.movie.MovieThumbnailGetVm;

import nlu.fit.movie_backend.viewmodel.recommendation.UserContext;
import nlu.fit.movie_backend.viewmodel.recommendation.UserFeedResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/recommendation")
@AllArgsConstructor
@CrossOrigin(origins = "*")
public class RecommendationController {
    private final RecommendationService recommendationService;

    @GetMapping("/personalized")
    public ResponseEntity<List<UserFeedResponse>> getUserFeed(@RequestBody UserContext userContext) {
        return ResponseEntity.ok(recommendationService.getUserFeed(userContext));
    }

    @PostMapping("/update")
    public ResponseEntity<?> updateRecommendations() {
        return ResponseEntity.ok(recommendationService.updateRecommendations());
    }

    @GetMapping("/similar/{movieId}")
    public ResponseEntity<List<MovieThumbnailGetVm>> getSimilarMovies(@PathVariable Long movieId) {
        return ResponseEntity.ok(recommendationService.getMovieSimilar(movieId));
    }
}
