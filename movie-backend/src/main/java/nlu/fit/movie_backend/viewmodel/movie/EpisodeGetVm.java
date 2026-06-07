package nlu.fit.movie_backend.viewmodel.movie;

import lombok.Builder;

@Builder
public record EpisodeGetVm(Long id, Integer seasonNumber, Integer episodeNumber, String title, String videoUrl, String stillPath,
 String overview) {
}