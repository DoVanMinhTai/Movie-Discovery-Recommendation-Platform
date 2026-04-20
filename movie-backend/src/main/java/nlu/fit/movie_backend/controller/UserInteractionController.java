package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.model.Rating;
import nlu.fit.movie_backend.service.JWTService;
import nlu.fit.movie_backend.service.RateService;
import nlu.fit.movie_backend.service.UserService;
import nlu.fit.movie_backend.viewmodel.rate.RatingPostVm;
import nlu.fit.movie_backend.viewmodel.user.OnboardingPostVm;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.Collections;
import java.util.Map;

@RestController
@RequestMapping("/user")
@AllArgsConstructor
public class UserInteractionController {
    private final UserService userService;
    private final RateService rateService;
    private final JWTService jwtService;

    @GetMapping("/api/getAllFavorites")
    public ResponseEntity<?> getFavorites(@RequestHeader("Authorization") String token) {
        String jwt = token.substring(7);
        Long userId = jwtService.extractUserId(jwt);
        return ResponseEntity.ok(userService.getAllMovieFavorites(userId));
    }

    @PostMapping("/api/favorites/add")
    public ResponseEntity<Map<String, String>> addFavorite(
            @RequestHeader("Authorization") String token,
            @RequestBody Long movieId) {

        String jwt = token.substring(7);
        Long userId = jwtService.extractUserId(jwt);

        userService.addFavorite(userId, movieId);
        return ResponseEntity.ok(Map.of("message", "Favorite added successfully"));
    }

    @DeleteMapping("/api/favorites/{movieId}")
    public ResponseEntity<Map<String, String>> deleteFavorite(@RequestHeader("Authorization") String token,
                                                              @PathVariable Long movieId) {
        String jwt = token.substring(7);
        Long userId = jwtService.extractUserId(jwt);

        userService.deleteFavorite(userId, movieId);
        return ResponseEntity.ok(Map.of("message", "Favorite deleted successfully"));
    }

    @PostMapping("/api/rateMovie")
    public ResponseEntity<Rating> rateMovie(
            @RequestHeader("Authorization") String token,
            @RequestBody RatingPostVm ratingRequest) {

        String jwt = token.substring(7);
        Long userId = jwtService.extractUserId(jwt);

        return ResponseEntity.ok(rateService.rateMovie(userId, ratingRequest));
    }

    @PostMapping("/onboarding")
    public ResponseEntity<Map<String, String>> onBoardingUser(
            @RequestBody OnboardingPostVm request,
            @AuthenticationPrincipal UserDetails userDetails
    ) {
        String email = userDetails.getUsername();
        String newToken = userService.processOnBoarding(email, request.genres());
        return ResponseEntity.ok(Collections.singletonMap("token", newToken));
    }

    @GetMapping("/api/checkWatchHistory/{mediaContentId}")
    public ResponseEntity<Boolean> checkWatchHistory(@RequestHeader("Authorization") String token, @PathVariable Long mediaContentId) {
        String tokenSub = token.substring(7);
        Long userId = jwtService.extractUserId(tokenSub);
        return ResponseEntity.ok(rateService.checkWatchHistory(userId, mediaContentId));
    }

}
