package nlu.fit.movie_backend.controller;

import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.constants.ApiEndpoints;
import nlu.fit.movie_backend.constants.ErrorCode;
import nlu.fit.movie_backend.service.AuthService;
import nlu.fit.movie_backend.service.JWTService;
import nlu.fit.movie_backend.viewmodel.auth.LoginPostVm;
import nlu.fit.movie_backend.viewmodel.auth.RegisterGetVm;
import nlu.fit.movie_backend.viewmodel.auth.RegisterPostVm;
import nlu.fit.movie_backend.exception.AppException;
import nlu.fit.movie_backend.viewmodel.ApiResponse;
import nlu.fit.movie_backend.viewmodel.user.ProfileGetVm;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.security.auth.login.AccountLockedException;

@RestController
@AllArgsConstructor
@CrossOrigin(origins = "${app.cors.allowed-origins}")
public class AuthController {
    private final AuthService authService;
    private final JWTService jWTService;

    @PostMapping(ApiEndpoints.Auth.REGISTER)
    public ResponseEntity<ApiResponse<RegisterGetVm>> registerUser(@RequestBody @Valid RegisterPostVm registerRequest) {
        return ResponseEntity.ok(ApiResponse.<RegisterGetVm>builder()
                .result(authService.register(registerRequest))
                .build());
    }

    @PostMapping(ApiEndpoints.Auth.LOGIN)
    public ResponseEntity<ApiResponse<ProfileGetVm>> loginUser(@RequestBody @Valid LoginPostVm loginPostVm) {
        return ResponseEntity.ok(ApiResponse.<ProfileGetVm>builder()
                .result(authService.login(loginPostVm))
                .build());
    }

    @GetMapping(ApiEndpoints.Auth.PROFILE)
    public ResponseEntity<ApiResponse<ProfileGetVm>> getProfile(@RequestHeader("Authorization") String authHeader) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            throw new AppException(ErrorCode.UNAUTHENTICATED);
        }
        String token = authHeader.substring(7);
        Long userId = jWTService.extractUserId(token);
        return ResponseEntity.ok(ApiResponse.<ProfileGetVm>builder()
                .result(authService.getProfile(userId))
                .build());
    }

    @GetMapping(ApiEndpoints.Auth.EXIST_EMAIL)
    public ResponseEntity<ApiResponse<Boolean>> existEmail(String email) {
        return ResponseEntity.ok(ApiResponse.<Boolean>builder().result(authService.existEmail(email.trim().toLowerCase())).build());
    }
}