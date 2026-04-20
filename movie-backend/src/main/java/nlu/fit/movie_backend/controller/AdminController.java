package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.service.AdminService;
import nlu.fit.movie_backend.service.MovieService;
import nlu.fit.movie_backend.service.UserService;
import nlu.fit.movie_backend.viewmodel.admin.AdminStatsResponse;
import nlu.fit.movie_backend.viewmodel.admin.AiStatusResponse;
import nlu.fit.movie_backend.viewmodel.admin.UserResponse;
import nlu.fit.movie_backend.viewmodel.movie.MoviePostVm;
import nlu.fit.movie_backend.viewmodel.movie.MoviePutVm;
import nlu.fit.movie_backend.viewmodel.movie.MovieThumbnailGetVm;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/admin")
@AllArgsConstructor
@CrossOrigin(origins = "${app.cors.allowed-origins}")
public class AdminController {
    private final MovieService movieService;
    private final UserService userService;
    private final AdminService adminService;

    @GetMapping("/movie/statistics")
    public ResponseEntity<AdminStatsResponse> getStatistics() {
        return ResponseEntity.ok(adminService.getStatistics());
    }

    @GetMapping("/movie/users")
    public ResponseEntity<List<UserResponse>> getAllUsers() {
        return ResponseEntity.ok(adminService.getAllUsers());
    }

    @DeleteMapping("/movie/users/{id}")
    public ResponseEntity<?> deleteUser(@PathVariable Long id) {
        return ResponseEntity.ok(userService.deleteUser(id));
    }

    @GetMapping("/movie/movies")
    public ResponseEntity<List<MovieThumbnailGetVm>> getAllMoviesForAdmin() {
        return ResponseEntity.ok(movieService.getAllMovies());
    }

    @PostMapping("/movie/addMovie")
    public ResponseEntity<?> addMovie(@RequestBody @Validated MoviePostVm movieRequest) {
        return ResponseEntity.ok(movieService.addMovie(movieRequest));
    }

    @PutMapping("/movie/putMovie")
    public ResponseEntity<?> updateMovie(@RequestBody @Validated MoviePutVm request) {
        return ResponseEntity.ok(movieService.putMovie(request));
    }

    @DeleteMapping("/movie/{id}")
    public ResponseEntity<Void> deleteMovie(@PathVariable Long id) {
        movieService.deleteMovie(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/movie/ai-status")
    public ResponseEntity<AiStatusResponse> getAiStatus() {
        return ResponseEntity.ok(adminService.getAiStatus());
    }

    @PostMapping("/movie/retrain-ai")
    public ResponseEntity<Map<String, String>> retrainAi() {
        return ResponseEntity.ok(adminService.triggerRetrain());
    }
}
