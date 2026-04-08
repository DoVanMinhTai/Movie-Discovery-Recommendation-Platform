package nlu.fit.movie_backend.viewmodel.movie;

import lombok.Builder;

@Builder
public record MovieHeroGetVm(
        Long id,
        String title,
        String description,
        String backdropUrl,
        String overview,
        String trailerKey
) {
}
