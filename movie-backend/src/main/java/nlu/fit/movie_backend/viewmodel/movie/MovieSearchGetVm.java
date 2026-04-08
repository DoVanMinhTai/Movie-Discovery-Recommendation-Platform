package nlu.fit.movie_backend.viewmodel.movie;

import lombok.Builder;

@Builder
public record MovieSearchGetVm(
        Long id, String title, Long releaseDate, String backdropPath
) {
}
