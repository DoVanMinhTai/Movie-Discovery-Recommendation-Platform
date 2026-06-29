package nlu.fit.movie_backend.service;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.model.User;
import nlu.fit.movie_backend.model.enumeration.ROLE;
import nlu.fit.movie_backend.repository.jpa.AuthRepository;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UsernameNotFoundException;

@org.springframework.stereotype.Service
@AllArgsConstructor
public class CustomUserDetailService implements org.springframework.security.core.userdetails.UserDetailsService {

    private final AuthRepository authRepository;

    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        User user = authRepository.findByEmail(email);

        if (user == null) {
            throw new UsernameNotFoundException("Không tìm thấy người dùng với email: " + email);
        }
        ROLE roleName = (user.getRole() != null) ? user.getRole() : ROLE.USER;

        return org.springframework.security.core.userdetails.User.builder().username(user.getUserName()).password(user.getPassword()).authorities(new SimpleGrantedAuthority("ROLE_" + roleName))
                .build();
    }
}
