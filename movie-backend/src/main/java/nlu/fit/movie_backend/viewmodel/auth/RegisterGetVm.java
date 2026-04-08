package nlu.fit.movie_backend.viewmodel.auth;

import lombok.Builder;

@Builder
public record RegisterGetVm(
        Long id,
        String userName,
        String email
) {
}
