package nlu.fit.movie_backend.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import nlu.fit.movie_backend.model.*;
import nlu.fit.movie_backend.model.enumeration.CONTENTTYPE;
import nlu.fit.movie_backend.model.enumeration.SORTBY;
import nlu.fit.movie_backend.repository.jpa.*;
import nlu.fit.movie_backend.viewmodel.movie.*;
import org.springframework.data.domain.*;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class MovieService {

    private final MovieRepository movieRepository;
    private final GenreRepository genreRepository;
    private final MediaContentRepository mediaContentRepository;
    private final UserRepository userRepository;

    public List<MovieThumbnailVms> getAllMovies() {
        List<Movie> movies = movieRepository.findAll();
        return fromListMoviesToListMovieThumbnailVms(movies);
    }

    public MovieDetailGetVm addMovie(MoviePostVm moviePostVm) {
        Movie movie = new Movie();
        movie.setTmDBId(moviePostVm.tmDBId());
        movie.setTitle(moviePostVm.title());
        movie.setOriginalTitle(moviePostVm.originalTitle());
        movie.setOverview(moviePostVm.overview());
        movie.setReleaseDate(moviePostVm.releaseDate());
        movie.setPosterPath(moviePostVm.posterPath());
        movie.setBackdropPath(moviePostVm.backdropPath());
        movie.setRuntime(moviePostVm.runtime());
        movie.setTrailerKey(moviePostVm.trailerKey());
        movie.setVoteAverage(moviePostVm.voteAverage());
        movie.setVoteCount(moviePostVm.voteCount());
        movie.setPopularity(moviePostVm.popularity());

        List<Genre> genres = genreRepository.findAllById(moviePostVm.genresId());

        movie.setGenres(genres);
        Movie savedMovie = movieRepository.save(movie);
        return fromMovieToMovieGetVm(savedMovie);
    }

    public MovieDetailGetVm putMovie(MoviePutVm request) {
        Movie movie = movieRepository.findById(request.id()).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
        MoviePostVm moviePostVm = request.moviePostVm();
        movie.setTmDBId(moviePostVm.tmDBId());
        movie.setTitle(moviePostVm.title());
        movie.setOriginalTitle(moviePostVm.originalTitle());
        movie.setOverview(moviePostVm.overview());
        movie.setReleaseDate(moviePostVm.releaseDate());
        movie.setPosterPath(moviePostVm.posterPath());
        movie.setBackdropPath(moviePostVm.backdropPath());
        movie.setRuntime(moviePostVm.runtime());
        movie.setTrailerKey(moviePostVm.trailerKey());
        movie.setVoteAverage(moviePostVm.voteAverage());
        movie.setVoteCount(moviePostVm.voteCount());
        movie.setPopularity(moviePostVm.popularity());
        Movie movieSaved = movieRepository.save(movie);
        return fromMovieToMovieGetVm(movieSaved);
    }

    public Void deleteMovie(Long id) {
        Movie movie = movieRepository.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
        movie.setDeleted(true);
        movieRepository.save(movie);
        return null;
    }

    public MediaContentGetVm getMediaContentById(Long id) {
        MediaContent mediaContent = mediaContentRepository.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));

        if (mediaContent instanceof Movie movie) {
            return MediaContentGetVm.builder()
                    .movieDetailVm(fromMovieToMovieGetVm(movie))
                    .seriesDetailVm(null)
                    .type("MOVIE")
                    .build();
        } else if (mediaContent instanceof Series series) {
            return MediaContentGetVm.builder()
                    .movieDetailVm(null)
                    .seriesDetailVm(fromSeriesToSeriesDetailVm(series))
                    .type("SERIES")
                    .build();
        }

        throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Unknown media type");
    }

    private SeriesDetailVm fromSeriesToSeriesDetailVm(Series series) {
        String genresName = series.getGenres()
                .stream()
                .map(Genre::getName)
                .collect(Collectors.joining(", "));
        List<SeasonVm> seasonVms = series.getSeasons().stream().map(item -> {
            List<EpisodeVm> episodeVmList = item.getEpisodes().stream().map(episode -> new EpisodeVm(
                    episode.getId(), episode.getSeasonNumber(), episode.getEpisodeNumber(), episode.getTitle(), episode.getVideoUrl(), episode.getStillPath()
            )).collect(Collectors.toList());
            return new SeasonVm(
                    item.getId(), item.getSeasonNumber(), item.getAirDate(), episodeVmList
            );
        }).collect(Collectors.toList());

        return new SeriesDetailVm(
                series.getId(),
                series.getTitle(),
                series.getBackdropPath(),
                "year",
                genresName,
                series.getOverview(),
                "cast",
                "director",
                series.getVoteAverage(),
                seasonVms
        );
    }

    private MovieDetailGetVm fromMovieToMovieGetVm(Movie movie) {
        String genresName = movie.getGenres()
                .stream()
                .map(Genre::getName)
                .collect(Collectors.joining(", "));

        return new MovieDetailGetVm(
                movie.getId(),
                movie.getTitle(),
                movie.getBackdropPath(),
                movie.getTrailerKey(),
                "year",
                String.valueOf(movie.getRuntime()),
                genresName,
                movie.getOverview(),
                "cast",
                "director",
                movie.getVoteAverage(),
                movie.getVideoUrl(),
                movie.getPosterPath()
        );
    }

    private List<MovieThumbnailVms> fromListMoviesToListMovieThumbnailVms(List<Movie> movies) {
        return movies.stream().map(item -> new MovieThumbnailVms(item.getId(), item.getTitle(), item.getBackdropPath())).toList();
    }

    public List<MovieThumbnailVms> getLatestMovies(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("releaseDate").descending());
        return movieRepository.findAllByIsDeletedFalse(false, pageable).stream().map(item -> new MovieThumbnailVms(item.getId(), item.getTitle(), item.getBackdropPath())).toList();
    }

    public List<MovieThumbnailVms> getMovieTrending(int limit) {
        return mediaContentRepository.findAll(Sort.by(Sort.Direction.DESC, "popularity"))
                .stream()
                .filter(media -> !media.isDeleted())
                .limit(limit)
                .map(media -> new MovieThumbnailVms(
                        media.getId(),
                        media.getTitle(),
                        media.getBackdropPath()
                ))
                .collect(Collectors.toList());
    }

    public List<Genre> getAllGenres() {
        return genreRepository.findAll();
    }

    public Page<MovieThumbnailVms> filterMovies(String sortBy, String genreId, int page, int size) {
        Sort sort = switch (SORTBY.valueOf(sortBy.toUpperCase())) {
            case NEWEST -> Sort.by("releaseDate").descending();
            case OLDEST -> Sort.by("releaseDate").ascending();
            case POPULARITY -> Sort.by("popularity").descending();
            case RATING -> Sort.by("voteAverage").descending();
            default -> Sort.by("id").descending();
        };

        Pageable pageable = PageRequest.of(page, size, sort);
        Page<MediaContent> mediaContents;
        if (genreId != null) {
            mediaContents = mediaContentRepository.findByGenresId(Long.valueOf(genreId), pageable);
        } else {
            mediaContents = mediaContentRepository.findAll(pageable);
        }
        return mediaContents.map(item -> new MovieThumbnailVms(item.getId(), item.getTitle(), item.getBackdropPath()));
    }

    public List<MovieThumbnailVms> getTop10(CONTENTTYPE contenttype, int limit) {
        return mediaContentRepository.findAllByDtype(contenttype.name()).stream()
                .filter(item -> !item.isDeleted())
                .sorted((a, b) -> Double.compare(b.getVoteCount(), a.getVoteCount()))
                .map(item -> new MovieThumbnailVms(item.getId(), item.getTitle(), item.getBackdropPath()))
                .limit(10)
                .collect(Collectors.toList());
    }

    public MovieHeroVm getMovieHero() {
        List<MediaContent> topMovies = mediaContentRepository.findGlobalTrending(PageRequest.of(0, 5));
        if (topMovies.isEmpty()) return null;

        MediaContent randomHero = topMovies.get(new Random().nextInt(topMovies.size()));
        Movie movie = (Movie) randomHero;
        return new MovieHeroVm(
                randomHero.getId(),
                randomHero.getTitle(),
                randomHero.getOriginalTitle(),
                randomHero.getBackdropPath(),
                randomHero.getOverview(),
                movie.getTrailerKey()
        );
    }

    public Map<String, List<MovieThumbnailVms>> getMoviePreferredGenres(Long userId, int limit) {
        User user = userRepository.findById(userId).orElse(null);
        Pageable pageable = PageRequest.of(0, limit);
        List<Long> genreIds = user.getPreferredGenres().stream().map(Genre::getId).toList();
        List<MediaContent> allMovies = mediaContentRepository.findAllByGenreIds(genreIds);
        return user.getPreferredGenres().stream()
                .collect(Collectors.toMap(
                        Genre::getName,
                        genre -> allMovies.stream()
                                .filter(m -> m.getGenres().contains(genre))
                                .limit(limit)
                                .map(item -> new MovieThumbnailVms(item.getId(), item.getTitle(), item.getBackdropPath()))
                                .collect(Collectors.toList())
                ));
    }

}
