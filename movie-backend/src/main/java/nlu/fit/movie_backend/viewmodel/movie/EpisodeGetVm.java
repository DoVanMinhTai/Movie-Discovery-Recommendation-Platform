package nlu.fit.movie_backend.viewmodel.movie;

import lombok.Builder;

@Builder
public record EpisodeGetVm(
        Long id,
        int seasonNumber,
        int episodeNumber,
        String title,
        String videoUrl,
        String stillPath
) {
}
