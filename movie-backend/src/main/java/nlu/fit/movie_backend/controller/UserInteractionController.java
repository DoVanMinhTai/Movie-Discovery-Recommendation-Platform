package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.constants.ApiEndpoints;
import nlu.fit.movie_backend.model.Rating;
import nlu.fit.movie_backend.service.JWTService;
import nlu.fit.movie_backend.service.RateService;
import nlu.fit.movie_backend.service.UserService;
import nlu.fit.movie_backend.viewmodel.ApiResponse;
import nlu.fit.movie_backend.viewmodel.rate.RatingPostVm;
import nlu.fit.movie_backend.viewmodel.user.MovieInteractionRequest;
import nlu.fit.movie_backend.viewmodel.user.OnboardingPostVm;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.Collections;
import java.util.Map;

@RestController
@AllArgsConstructor
@CrossOrigin(origins = "${app.cors.allowed-origins}")
public class UserInteractionController {
    private final UserService userService;
    private final RateService rateService;
    private final JWTService jwtService;

    @GetMapping(ApiEndpoints.UserInteraction.GET_ALL_FAVORITE)
    public ResponseEntity<ApiResponse<?>> getFavorites(@RequestHeader("Authorization") String token) {
        String jwt = token.substring(7);
        Long userId = jwtService.extractUserId(jwt);
        System.out.println(userService.getAllMovieFavorites(userId));
        return ResponseEntity.ok(ApiResponse.builder().result(userService.getAllMovieFavorites(userId)).build());
    }

    @PostMapping(ApiEndpoints.UserInteraction.ADD_MOVIE_FAVORITE)
    public ResponseEntity<ApiResponse<Map<String, String>>> addFavorite(
            @RequestHeader("Authorization") String token,
            @RequestBody MovieInteractionRequest request) {

        String jwt = token.substring(7);
        Long userId = jwtService.extractUserId(jwt);

        userService.addFavorite(userId, request.movieId());
        return ResponseEntity.ok(ApiResponse.<Map<String, String>>builder().result(Map.of("message", "Favorite added successfully")).build());
    }

    @DeleteMapping(ApiEndpoints.UserInteraction.DELETE_MOVIE_FAVORITE)
    public ResponseEntity<ApiResponse<Map<String, String>>> deleteFavorite(@RequestHeader("Authorization") String token,
                                                              @PathVariable Long movieId) {
        String jwt = token.substring(7);
        Long userId = jwtService.extractUserId(jwt);

        userService.deleteFavorite(userId, movieId);
        return ResponseEntity.ok(ApiResponse.<Map<String, String>>builder().result(Map.of("message", "Favorite deleted successfully")).build());
    }

    @PostMapping(ApiEndpoints.UserInteraction.ADD_RATE)
    public ResponseEntity<ApiResponse<Rating>> rateMovie(
            @RequestHeader("Authorization") String token,
            @RequestBody RatingPostVm ratingRequest) {

        String jwt = token.substring(7);
        Long userId = jwtService.extractUserId(jwt);

        return ResponseEntity.ok(ApiResponse.<Rating>builder().result(rateService.rateMovie(userId, ratingRequest)).build());
    }

    @PostMapping(ApiEndpoints.UserInteraction.ONBOARDING)
    public ResponseEntity<ApiResponse<Map<String, String>> >onBoardingUser(
            @RequestBody OnboardingPostVm request,
            @AuthenticationPrincipal UserDetails userDetails
    ) {
        String email = userDetails.getUsername();
        String newToken = userService.processOnBoarding(email, request.genres());
        return ResponseEntity.ok(ApiResponse.<Map<String, String>>builder().result(Collections.singletonMap("token", newToken)).build());
    }

    @GetMapping(ApiEndpoints.UserInteraction.EXISTS_WATCH_HISTORY)
    public ResponseEntity<ApiResponse<Boolean>> checkWatchHistory(@RequestHeader("Authorization") String token, @PathVariable Long mediaContentId) {
        String tokenSub = token.substring(7);
        Long userId = jwtService.extractUserId(tokenSub);
        return ResponseEntity.ok(ApiResponse.<Boolean>builder().result(rateService.checkWatchHistory(userId, mediaContentId)).build());
    }

    @GetMapping(ApiEndpoints.UserInteraction.GET_RATE)
    public ResponseEntity<ApiResponse<?>> getRating(@RequestHeader("Authorization") String token, @PathVariable Long mediaContentId) {
        String tokenSub = token.substring(7);
        Long userId = jwtService.extractUserId(tokenSub);
        return ResponseEntity.ok(ApiResponse.builder().result(rateService.getRating(userId, mediaContentId)).build());
    }

    @PostMapping(ApiEndpoints.UserInteraction.ADD_WATCH_HISTORY)
    public ResponseEntity<ApiResponse<Map<String, String>>> addToWatchHistory(@RequestHeader("Authorization") String token, @RequestBody MovieInteractionRequest request) {
        String tokenSub = token.substring(7);
        Long userId = jwtService.extractUserId(tokenSub);
        rateService.addToWatchHistory(userId, request.movieId());
        return ResponseEntity.ok(ApiResponse.<Map<String, String>>builder().result(Map.of("message", "Watch history updated successfully")).build());
    }

}
