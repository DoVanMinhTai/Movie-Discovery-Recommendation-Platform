package nlu.fit.movie_backend.viewmodel.movie;

import lombok.Builder;

@Builder
public record MediaContentGetVm(
        MovieDetailGetVm movieDetailVm,
        SeriesDetailVm seriesDetailVm,
        String type
) {
}
