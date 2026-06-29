package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.constants.ApiEndpoints;
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

import nlu.fit.movie_backend.viewmodel.ApiResponse;
import org.springframework.format.annotation.DateTimeFormat;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

import org.springframework.data.domain.Page;

@RestController
@RequestMapping()
@AllArgsConstructor
@CrossOrigin(origins = "${app.cors.allowed-origins}")
public class AdminController {
    private final MovieService movieService;
    private final UserService userService;
    private final AdminService adminService;

    @GetMapping(ApiEndpoints.Admin.STATISTICS)
    public ResponseEntity<ApiResponse<AdminStatsResponse>> getStatistics(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate from,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate to) {
        return ResponseEntity.ok(ApiResponse.<AdminStatsResponse>builder()
                .result(adminService.getStatistics(from, to))
                .build());
    }

    @GetMapping(ApiEndpoints.Admin.CHECK_DUPLICATE)
    public ResponseEntity<ApiResponse<Map<String, Boolean>>> checkDuplicate(
            @RequestParam String title,
            @RequestParam int year,
            @RequestParam(required = false) Long excludeId) {
        boolean isDuplicate = adminService.checkDuplicate(title, year, excludeId);
        return ResponseEntity.ok(ApiResponse.<Map<String, Boolean>>builder()
                .result(Map.of("isDuplicate", isDuplicate))
                .build());
    }

    @GetMapping(ApiEndpoints.Admin.USERS)
    public ResponseEntity<ApiResponse<List<UserResponse>>> getAllUsers() {
        return ResponseEntity.ok(ApiResponse.<List<UserResponse>>builder()
                .result(adminService.getAllUsers())
                .build());
    }

    @DeleteMapping(ApiEndpoints.Admin.DELETE_USER)
    public ResponseEntity<ApiResponse<Object>> deleteUser(@PathVariable Long id) {
        return ResponseEntity.ok(ApiResponse.<Object>builder()
                .result(userService.deleteUser(id))
                .build());
    }

    @GetMapping(ApiEndpoints.Admin.MOVIES)
    public ResponseEntity<ApiResponse<List<MovieThumbnailGetVm>>> getAllMoviesForAdmin() {
        return ResponseEntity.ok(ApiResponse.<List<MovieThumbnailGetVm>>builder()
                .result(movieService.getAllMovies())
                .build());
    }

    @PostMapping(ApiEndpoints.Admin.ADD_MOVIE)
    public ResponseEntity<ApiResponse<Object>> addMovie(@RequestBody @Validated MoviePostVm movieRequest, @RequestHeader("X-Admin-Password") String adminPassword) {
        if (!"adminadmin".equals(adminPassword)) {
            return ResponseEntity.status(403).body(ApiResponse.<Object>builder()
                    .message("Mật khẩu Admin không chính xác!")
                    .code(1005)
                    .build());
        }
        return ResponseEntity.ok(ApiResponse.<Object>builder()
                .result(movieService.addMovie(movieRequest))
                .build());
    }

    @PutMapping(ApiEndpoints.Admin.UPDATE_MOVIE)
    public ResponseEntity<ApiResponse<Object>> updateMovie(@RequestBody @Validated MoviePutVm request, @RequestHeader("X-Admin-Password") String adminPassword) {
        if (!"adminadmin".equals(adminPassword)) {
            return ResponseEntity.status(403).body(ApiResponse.<Object>builder()
                    .message("Mật khẩu Admin không chính xác!")
                    .code(1005)
                    .build());
        }
        return ResponseEntity.ok(ApiResponse.<Object>builder()
                .result(movieService.putMovie(request))
                .build());
    }

    @DeleteMapping(ApiEndpoints.Admin.DELETE_MOVIE)
    public ResponseEntity<ApiResponse<Object>> deleteMovie(@PathVariable Long id, @RequestHeader("X-Admin-Password") String adminPassword) {
        if (!"adminadmin".equals(adminPassword)) {
            return ResponseEntity.status(403).body(ApiResponse.<Object>builder()
                    .message("Mật khẩu Admin không chính xác!")
                    .code(1005)
                    .build());
        }
        movieService.deleteMovie(id);
        return ResponseEntity.ok(ApiResponse.<Object>builder()
                .message("Đã xóa phim thành công!")
                .build());
    }

//    @GetMapping(ApiEndpoints.Admin.AI_STATUS)
//    public ResponseEntity<AiStatusResponse> getAiStatus() {
//        return ResponseEntity.ok(adminService.getAiStatus());
//    }
//
//    @PostMapping(ApiEndpoints.Admin.RETRAIN_AI)
//    public ResponseEntity<?> updateRecommendations() {
//        try {
//            new ProcessBuilder("python", "scripts/cf/sync_data/sync_item_vectors.py")
//                    .directory(new java.io.File("F:/project_SW/Media-Recommender-System/movie-recommendation"))
//                    .start();
//
//            return ResponseEntity.ok(Map.of("message", "Data synchronization and AI training started in background."));
//        } catch (Exception e) {
//            return ResponseEntity.status(500).body("Failed to start synchronization: " + e.getMessage());
//        }
//    }
}
