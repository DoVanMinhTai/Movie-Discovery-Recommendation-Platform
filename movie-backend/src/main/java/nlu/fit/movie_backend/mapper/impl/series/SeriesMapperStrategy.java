package nlu.fit.movie_backend.mapper.impl.series;

import nlu.fit.movie_backend.mapper.MediaMapper;
import nlu.fit.movie_backend.model.Genre;
import nlu.fit.movie_backend.model.MediaContent;
import nlu.fit.movie_backend.model.Series;
import nlu.fit.movie_backend.viewmodel.movie.EpisodeGetVm;
import nlu.fit.movie_backend.viewmodel.movie.MediaContentGetVm;
import nlu.fit.movie_backend.viewmodel.movie.SeasonGetVm;
import nlu.fit.movie_backend.viewmodel.movie.SeriesGetVm;

import java.util.List;
import java.util.stream.Collectors;

public class SeriesMapperStrategy implements MediaMapper {
    @Override
    public boolean supports(MediaContent mediaContent) {
        return mediaContent instanceof Series;
    }

    @Override
    public MediaContentGetVm map(MediaContent mediaContent) {
        Series series = (Series) mediaContent;

        return MediaContentGetVm.builder()
                .movieVm(null)
                .seriesVm(toDetailVm(series))
                .type("SERIES")
                .build();
    }

    private SeriesGetVm toDetailVm(Series series) {
        String genresName = series.getGenres()
                .stream()
                .map(Genre::getName)
                .collect(Collectors.joining(", "));
        List<SeasonGetVm> seasonVms = series.getSeasons().stream().map(item -> {
            List<EpisodeGetVm> episodeVmList = item.getEpisodes().stream().map(episode -> new EpisodeGetVm(
                    episode.getId(), episode.getSeasonNumber(), episode.getEpisodeNumber(), episode.getTitle(), episode.getVideoUrl(), episode.getStillPath()
            )).collect(Collectors.toList());
            return new SeasonGetVm(
                    item.getId(), item.getSeasonNumber(), item.getAirDate(), episodeVmList
            );
        }).collect(Collectors.toList());

        return new SeriesGetVm(
                series.getId(),
                series.getTitle(),
                series.getBackdropPath(),
                String.valueOf(series.getReleaseDate().getYear()),
                genresName,
                series.getOverview(),
                series.getCast(),
                series.getDirector(),
                series.getVoteAverage(),
                seasonVms
        );
    }
}
