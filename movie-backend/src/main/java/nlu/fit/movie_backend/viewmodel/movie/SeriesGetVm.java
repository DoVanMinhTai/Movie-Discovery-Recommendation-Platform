package nlu.fit.movie_backend.viewmodel.movie;

import lombok.Builder;

import java.util.List;

@Builder
public record SeriesGetVm(
        Long id,
        String title,
        String backdropUrl,
        String year,
        String genres,
        String description,
        String cast,
        String director,
        Double rating,
        List<SeasonGetVm> seasonVm
) {
}
