package nlu.fit.movie_backend.service;

import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import nlu.fit.movie_backend.mapper.impl.media.MediaMapperFactory;
import nlu.fit.movie_backend.mapper.impl.movie.MovieMapperStrategy;
import nlu.fit.movie_backend.mapper.impl.movie.MovieSortStrategy;
import nlu.fit.movie_backend.model.*;
import nlu.fit.movie_backend.model.enumeration.CONTENTTYPE;
import nlu.fit.movie_backend.repository.jpa.*;
import nlu.fit.movie_backend.viewmodel.movie.*;
import org.springframework.data.domain.*;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class MovieService {

    private final MediaContentRepository mediaContentRepository;
    private final MovieRepository movieRepository;
    private final UserRepository userRepository;
    private final GenreService genreService;
    private final MediaMapperFactory mediaMapperFactory;
    private final MovieMapperStrategy movieMapper;

    public List<MovieThumbnailGetVm> getAllMovies() {
        List<Movie> movies = movieRepository.findAll();
        return movieMapper.toThumbnailGetVmList(movies);
    }

    @Transactional
    public MovieGetVm addMovie(MoviePostVm moviePostVm) {
//      Validate field of Model

        Movie movie = movieMapper.toEntity(moviePostVm);

        List<Genre> genres = genreService.findAllById(moviePostVm.genresId());

        movie.setGenres(genres);

        return movieMapper.toDetailVm(movieRepository.save(movie));

    }

    @Transactional
    public MovieGetVm putMovie(MoviePutVm moviePutVm) {
        Movie existingMovie = movieRepository.findById(moviePutVm.id()).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));

        movieMapper.updateMovieFromVm(moviePutVm, existingMovie);

        movieMapper.toEntity(moviePutVm);

        Movie movieSaved = movieRepository.save(existingMovie);

        return movieMapper.toDetailVm(movieSaved);
    }

    @Transactional
    public void deleteMovie(Long id) {
        movieRepository.deleteById(id);
    }

    public MediaContentGetVm getMediaContentById(Long id) {
        MediaContent mediaContent = mediaContentRepository.findById(id).orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND));
        return mediaMapperFactory.getVm(mediaContent);
    }

    public List<MovieThumbnailGetVm> getLatestMovies(int page, int size) {
        MovieSortStrategy strategy = MovieSortStrategy.NEWEST;

        Pageable pageable = PageRequest.of(page, size, strategy.getSortConfig());

        return movieMapper.toThumbnailGetVmList(movieRepository.findAllByIsDeletedFalse(false, pageable));
    }

    public List<MovieThumbnailGetVm> getTrendingMovies(int limit) {
        MovieSortStrategy strategy = MovieSortStrategy.POPULARITY;

        Pageable pageable = PageRequest.of(0, limit, strategy.getSortConfig());

        Page<Movie> moviePage = movieRepository.findAll(pageable);

        return moviePage.getContent()
                .stream()
                .map(movieMapper::toThumbnailGetVm)
                .toList();
    }

    public List<MovieThumbnailGetVm> getTop10(CONTENTTYPE contenttype, int limit) {
        Pageable pageable = PageRequest.of(0, limit, Sort.by(Sort.Direction.DESC, "voteCount"));

        return movieRepository.findAllByDtypeAndIsDeletedFalse(contenttype.name(), pageable).getContent()
                .stream().map(movieMapper::toThumbnailGetVm).toList();
    }

    public MovieHeroGetVm getMovieHero() {
        List<Movie> topMovies = movieRepository.findGlobalTrending(PageRequest.of(0, 5));

        if (topMovies.isEmpty()) return null;

        return movieMapper.toHeroGetVm(topMovies.get(new Random().nextInt(topMovies.size())));
    }

    public Map<String, List<MovieThumbnailGetVm>> getMoviePreferredGenres(Long userId, int limit) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "User không tồn tại"));

        List<Genre> preferredGenres = user.getPreferredGenres().stream().toList();
        Map<String, List<MovieThumbnailGetVm>> result = new LinkedHashMap<>();
        for (Genre genre : preferredGenres) {
            Pageable pageable = PageRequest.of(0, limit, Sort.by("popularity").descending());

            List<MovieThumbnailGetVm> movies = movieRepository
                    .findByGenresIdAndIsDeletedFalse(genre.getId(), pageable)
                    .getContent()
                    .stream()
                    .map(movieMapper::toThumbnailGetVm)
                    .toList();

            result.put(genre.getName(), movies);
        }

        return result;
    }

    public Page<MovieThumbnailGetVm> filterMovies(String sortBy, String genreId, int page, int size) {
        MovieSortStrategy strategy = MovieSortStrategy.fromString(sortBy);
        Sort sort = strategy.getSortConfig();

        Pageable pageable = PageRequest.of(page, size, sort);

        Page<MediaContent> mediaContents;
        if (genreId != null) {
            mediaContents = mediaContentRepository.findByGenresId(Long.valueOf(genreId), pageable);
        } else {
            mediaContents = mediaContentRepository.findAll(pageable);
        }

        return mediaContents.map(item -> new MovieThumbnailGetVm(item.getId(), item.getTitle(), item.getBackdropPath()));
    }
}
