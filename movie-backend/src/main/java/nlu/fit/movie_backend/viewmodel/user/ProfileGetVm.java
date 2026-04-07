package nlu.fit.movie_backend.viewmodel.user;

import lombok.Builder;
import java.util.List;

@Builder
public record ProfileGetVm(
        Long id, String userName, String token,
        String fullName, String email, String role, String joinedDate, List<String> preferences
) {
}
