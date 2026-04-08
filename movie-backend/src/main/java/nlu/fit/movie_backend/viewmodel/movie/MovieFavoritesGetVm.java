package nlu.fit.movie_backend.viewmodel.movie;

import lombok.Builder;

@Builder
public record MovieFavoritesGetVm(
        Long id, String title, String posterPath
) {
}
