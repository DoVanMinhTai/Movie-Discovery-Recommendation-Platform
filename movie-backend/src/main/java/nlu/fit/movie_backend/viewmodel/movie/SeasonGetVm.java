package nlu.fit.movie_backend.viewmodel.movie;

import lombok.Builder;

import java.time.LocalDate;
import java.util.List;

@Builder
public record SeasonGetVm(
        Long id,
        int seasonNumber,
        LocalDate airDate,
        List<EpisodeGetVm> episodeVmList
) {
}
