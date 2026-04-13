package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.service.AuthService;
import nlu.fit.movie_backend.service.JWTService;
import nlu.fit.movie_backend.viewmodel.auth.LoginPostVm;
import nlu.fit.movie_backend.viewmodel.auth.RegisterGetVm;
import nlu.fit.movie_backend.viewmodel.auth.RegisterPostVm;
import nlu.fit.movie_backend.viewmodel.user.ProfileGetVm;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
@AllArgsConstructor
public class AuthController {
public class AuthController {
    private final AuthService authService;
    private final JWTService jWTService;

    @PostMapping("/register")
    public ResponseEntity<RegisterGetVm> registerUser(@RequestBody RegisterPostVm registerRequest) {
        RegisterGetVm registerResponse = authService.register(registerRequest);
        return ResponseEntity.ok(registerResponse);
    }

    @PostMapping("/login")
    public ResponseEntity<ProfileGetVm> loginUser(@RequestBody LoginPostVm loginPostVm) {
        ProfileGetVm loginResponse = authService.login(loginPostVm);
        return ResponseEntity.ok(loginResponse);
    }

    @GetMapping("/profile")
    public ResponseEntity<ProfileGetVm> getProfile(@RequestHeader("Authorization") String authHeader) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        String token = authHeader.substring(7);
        Long userId = jWTService.extractUserId(token);
        return ResponseEntity.ok(authService.getProfile(userId));
    }

    @GetMapping("/exist-email")
    public ResponseEntity<?> existEmail(String email) {
        return ResponseEntity.ok(authService.existEmail(email.trim().toLowerCase()));
    }
}