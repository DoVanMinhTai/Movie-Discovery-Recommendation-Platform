package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.constants.ApiEndpoints;
import nlu.fit.movie_backend.viewmodel.ApiResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import nlu.fit.movie_backend.service.RecommendationService;

import java.util.Map;

@RestController
@AllArgsConstructor
@CrossOrigin(origins = "${app.cors.allowed-origins}")
public class RecommendationController {
    private final RecommendationService recommendationService;

    @GetMapping(ApiEndpoints.Recommendation.GET_CF_USERID)
    public ResponseEntity<ApiResponse<?>> getCollaborativeFiltering(@PathVariable Long userId, @RequestParam(defaultValue = "10") int topN) {
        return ResponseEntity.ok(ApiResponse.builder().result(recommendationService.getCollaborativeFiltering(userId, topN)).build());
    }

    @GetMapping(ApiEndpoints.Recommendation.GET_CF_SIMILAR_BY_MOVIE_ID)
    public ResponseEntity<ApiResponse<?>> getSimilarMoviesCF(@PathVariable Long movieId, @RequestParam(defaultValue = "10") int topN) {
        return ResponseEntity.ok(ApiResponse.builder().result(recommendationService.getSimilarMoviesCF(movieId, topN)).build());
    }

    @GetMapping(ApiEndpoints.Recommendation.GET_CBF_SEARCH)
    public ResponseEntity<ApiResponse<?>> searchMoviesCBF(@RequestParam String query, @RequestParam(defaultValue = "10") int topN) {
        return ResponseEntity.ok(ApiResponse.builder().result(recommendationService.searchMoviesCBF(query, topN)).build());
    }

    @GetMapping(ApiEndpoints.Recommendation.GET_CBF_SIMILAR_BY_MOVIE_ID)
    public ResponseEntity<ApiResponse<?>> getSimilarMoviesCBF(@PathVariable Long movieId, @RequestParam(defaultValue = "10") int topN) {
        return ResponseEntity.ok(ApiResponse.builder().result(recommendationService.getSimilarMoviesCBF(movieId, topN)).build());
    }
    
    @GetMapping(ApiEndpoints.Recommendation.GET_HYBRID_RECOMMENDATION)
    public ResponseEntity<ApiResponse<?>> getHybridRecommendations(@PathVariable Long userId,
                                                      @RequestParam(required = false) Long movieId, 
                                                      @RequestParam(defaultValue = "10") int topN) {
        return ResponseEntity.ok(ApiResponse.builder().result(recommendationService.getHybridRecommendations(userId, movieId, topN)).build());
    }
}
