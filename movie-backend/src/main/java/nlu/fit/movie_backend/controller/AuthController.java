package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.service.AuthService;
import nlu.fit.movie_backend.service.JWTService;
import nlu.fit.movie_backend.viewmodel.auth.LoginVm;
import nlu.fit.movie_backend.viewmodel.auth.RegisterPostVm;
import nlu.fit.movie_backend.viewmodel.auth.RegisterVm;
import nlu.fit.movie_backend.viewmodel.user.ProfileVm;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
@AllArgsConstructor
@CrossOrigin(origins = "*")
public class AuthController {
    private final AuthService authService;
    private final JWTService jWTService;

    @PostMapping("/register")
    public ResponseEntity<RegisterVm> registerUser(@RequestBody RegisterPostVm registerRequest) {
        RegisterVm registerResponse = authService.register(registerRequest);
        return ResponseEntity.ok(registerResponse);
    }

    @PostMapping("/login")
    public ResponseEntity<ProfileVm> loginUser(@RequestBody LoginVm loginRequest) {
        ProfileVm loginResponse = authService.login(loginRequest);
        return ResponseEntity.ok(loginResponse);
    }

    @GetMapping("/profile")
    public ResponseEntity<ProfileVm> getProfile(
            @RequestHeader("Authorization") String authHeader
    ) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        String token = authHeader.substring(7);
        Long userId = jWTService.extractUserId(token);
        return ResponseEntity.ok(authService.getProfile(userId));
    }
}