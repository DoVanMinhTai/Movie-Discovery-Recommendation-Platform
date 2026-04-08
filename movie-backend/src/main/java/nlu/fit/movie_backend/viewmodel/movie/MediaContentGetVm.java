package nlu.fit.movie_backend.viewmodel.movie;

import lombok.Builder;

@Builder
public record MediaContentGetVm(
        MovieGetVm movieVm,
        SeriesGetVm seriesVm,
        String type
) {
}
