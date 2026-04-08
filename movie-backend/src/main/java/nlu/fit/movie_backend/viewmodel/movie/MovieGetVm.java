package nlu.fit.movie_backend.viewmodel.movie;

import lombok.Builder;

import java.util.List;

@Builder
public record MovieGetVm(
        Long id,
        String title,
        String backdropUrl,
        String trailerKey,
        String year,
        String duration,
        String genres,
        String description,
        String cast,
        String director,
        Double rating,
        String url,
        String posterPath
) {
}
