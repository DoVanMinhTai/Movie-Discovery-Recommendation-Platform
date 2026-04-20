package nlu.fit.movie_backend.service;

import lombok.RequiredArgsConstructor;
import nlu.fit.movie_backend.model.User;
import nlu.fit.movie_backend.model.UserToken;
import nlu.fit.movie_backend.repository.jpa.AuthRepository;
import nlu.fit.movie_backend.repository.jpa.TokenRepository;
import nlu.fit.movie_backend.repository.jpa.UserRepository;
import nlu.fit.movie_backend.viewmodel.auth.LoginPostVm;
import nlu.fit.movie_backend.viewmodel.auth.RegisterGetVm;
import nlu.fit.movie_backend.viewmodel.auth.RegisterPostVm;
import nlu.fit.movie_backend.viewmodel.user.ProfileGetVm;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import javax.security.auth.login.AccountLockedException;
import java.time.format.DateTimeFormatter;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AuthService {
    private final UserRepository userRepository;
    private final TokenRepository tokenRepository;
    private final AuthRepository authRepository;
    private final AuthenticationManager authenticationManager;
    private final PasswordEncoder passwordEncoder;
    private final JWTService JwtService;

    public RegisterGetVm register(RegisterPostVm request) {
        User user = new User();
        user.setUserName(request.userName());
        user.setEmail(request.email());
        user.setPassword(passwordEncoder.encode(request.password()));
        user = authRepository.save(user);
        return RegisterGetVm.builder()
                .id(user.getId())
                .userName(user.getUserName())
                .email(user.getEmail()).build();
    }

    public ProfileGetVm login(LoginPostVm loginPostVm) throws AccountLockedException {
        String email = loginPostVm.email();
        String password = loginPostVm.password();
        User user = authRepository.findByEmail(email);

        if (user == null) {
//                throw new ResourceNotFoundException("Email/username không tồn tại");
        }

        if (!user.isActive()) {
            throw new AccountLockedException("Tài khoản của bạn đã bị khóa");
        }

        try {

            var authentication = authenticationManager.authenticate(
                    new org.springframework.security.authentication.UsernamePasswordAuthenticationToken(
                            email,
                            password));
            SecurityContextHolder.getContext().setAuthentication(authentication);


            String jwt = JwtService.generateJWTToken(user);
            UserToken token = new UserToken();
            token.setToken(jwt);
            token.setUser(user);
            token.setRevoked(false);
            tokenRepository.save(token);
            return ProfileGetVm.builder()
                    .id(user.getId())
                    .userName(user.getUserName())
                    .email(user.getEmail())
                    .role(String.valueOf(user.getRole()))
                    .token(jwt)
                    .build();
        } catch (BadCredentialsException e) {
            throw new BadCredentialsException("Mật khẩu không chính xác");

        }
    }

    public ProfileGetVm getProfile(Long userId) {
        User user = userRepository.findById(userId).orElseThrow();

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss");
        String formattedDate = (user.getJoinedDate() != null)
                ? user.getJoinedDate().format(formatter)
                : null;

        return ProfileGetVm.builder()
                .id(user.getId())
                .userName(user.getUserName())
                .fullName(user.getFullName())
                .email(user.getEmail())
                .role(String.valueOf(user.getRole()))
                .preferences(user.getPreferredGenres().stream().map(
                                item -> item.getName())
                        .collect(Collectors.toList()))
                .joinedDate(formattedDate)
                .build();
    }

    public Boolean existEmail(String email) {
        return userRepository.existsByEmailAndIsDeletedFalse(email);
    }
}
