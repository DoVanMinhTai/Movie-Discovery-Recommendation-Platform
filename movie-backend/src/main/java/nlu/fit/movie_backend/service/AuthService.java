package nlu.fit.movie_backend.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
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

import nlu.fit.movie_backend.constants.ErrorCode;
import nlu.fit.movie_backend.exception.AppException;

import java.time.format.DateTimeFormatter;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class AuthService {
    private final UserRepository userRepository;
    private final TokenRepository tokenRepository;
    private final AuthRepository authRepository;
    private final AuthenticationManager authenticationManager;
    private final PasswordEncoder passwordEncoder;
    private final JWTService JwtService;

    public RegisterGetVm register(RegisterPostVm request) {
        if (userRepository.existsByEmailAndIsDeletedFalse(request.email())) {
            throw new AppException(ErrorCode.USER_EXISTED);
        }

        if (request.password().length() < 8) {
            throw new AppException(ErrorCode.PASSWORD_INVALID);
        }

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

    public ProfileGetVm login(LoginPostVm loginPostVm) {
        String email = loginPostVm.email();
        String password = loginPostVm.password();
        User user = authRepository.findByEmail(email);

        if (user == null) {
            throw new AppException(ErrorCode.USER_NOT_EXISTED);
        }

        if (user.isDeleted()) {
            throw new AppException(ErrorCode.ACCOUNT_LOCKED);
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
            throw new AppException(ErrorCode.INVALID_CREDENTIALS);
        }
    }

    public ProfileGetVm getProfile(Long userId) {
        User user = userRepository.findById(userId).orElseThrow(() ->
                new AppException(ErrorCode.USER_NOT_FOUND));

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
