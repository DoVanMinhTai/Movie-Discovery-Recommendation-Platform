package nlu.fit.movie_backend.mapper.impl.movie;

import nlu.fit.movie_backend.mapper.MediaMapper;
import nlu.fit.movie_backend.model.Genre;
import nlu.fit.movie_backend.model.MediaContent;
import nlu.fit.movie_backend.model.Movie;
import nlu.fit.movie_backend.model.enumeration.CONTENTTYPE;
import nlu.fit.movie_backend.viewmodel.movie.*;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.stream.Collectors;

@Component
public class MovieMapperStrategy implements MediaMapper {
    public Movie toEntity(MoviePostVm dto) {
        Movie movie = new Movie();
        BeanUtils.copyProperties(dto, movie);
        return movie;
    }

    public Movie toEntity(MoviePutVm dto) {
        Movie movie = new Movie();
        BeanUtils.copyProperties(dto, movie);
        return movie;
    }

    public MovieGetVm toDetailVm(Movie movie) {
        String genresName = movie.getGenres().stream()
                .map(Genre::getName)
                .collect(Collectors.joining(", "));

        return new MovieGetVm(
                movie.getId(),
                movie.getTitle(),
                movie.getBackdropPath(),
                movie.getTrailerKey(),
                String.valueOf(movie.getReleaseDate().getYear()),
                String.valueOf(movie.getRuntime()),
                genresName,
                movie.getOverview(),
                movie.getCast(),
                movie.getDirector(),
                movie.getVoteAverage(),
                movie.getVideoUrl(),
                movie.getPosterPath()
        );
    }

    public List<MovieThumbnailGetVm> toThumbnailGetVmList(List<Movie> movies) {
        return movies.stream().map(
                item -> new MovieThumbnailGetVm(item.getId(), item.getTitle(), item.getBackdropPath())).toList();
    }

    public MovieThumbnailGetVm toThumbnailGetVm(Movie movie) {
        return new MovieThumbnailGetVm(
                movie.getId(),
                movie.getTitle(),
                movie.getBackdropPath()
        );
    }

    public MovieHeroGetVm toHeroGetVm(Movie movie) {
        return new MovieHeroGetVm(
                movie.getId(),
                movie.getTitle(),
                movie.getOriginalTitle(),
                movie.getBackdropPath(),
                movie.getOverview(),
                movie.getTrailerKey()
        );
    }

    public void updateMovieFromVm(MoviePutVm moviePutVm, Movie movie) {
        MoviePostVm data = moviePutVm.moviePostVm();
        movie.setTmDBId(data.tmDBId());
        movie.setTitle(data.title());
        movie.setOriginalTitle(data.originalTitle());
        movie.setOverview(data.overview());
        movie.setReleaseDate(data.releaseDate());
        movie.setPosterPath(data.posterPath());
        movie.setBackdropPath(data.backdropPath());
        movie.setRuntime(data.runtime());
        movie.setTrailerKey(data.trailerKey());
        movie.setVoteAverage(data.voteAverage());
        movie.setVoteCount(data.voteCount());
        movie.setPopularity(data.popularity());
    }

    @Override
    public boolean supports(MediaContent mediaContent) {
        return mediaContent instanceof Movie;
    }

    @Override
    public MediaContentGetVm map(MediaContent mediaContent) {
        Movie movie = (Movie) mediaContent;
        return MediaContentGetVm.builder()
                .movieVm(toDetailVm(movie))
                .seriesVm(null)
                .type(String.valueOf(CONTENTTYPE.MOVIE))
                .build();
    }
}