package nlu.fit.movie_backend.service;

import lombok.RequiredArgsConstructor;
import nlu.fit.movie_backend.repository.elasticsearchrepository.MediaContentSearchRepository;
import nlu.fit.movie_backend.viewmodel.movie.MovieSearchGetVm;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.List;
import java.util.stream.Collectors;


@Service
@RequiredArgsConstructor
public class SearchService {
    private final MediaContentSearchRepository mediaContentSearchRepository;

    public List<MovieSearchGetVm> getMovieSuggestionByTitle(String input) {
        String sanitized = input.replaceAll("[\\*\\\"\\?\\~]", "").trim();
        return mediaContentSearchRepository.findAllByTitleContaining(sanitized).stream().map(item -> {
            Instant instant = Instant.ofEpochMilli(item.getReleaseDate());
            Long year = (long) LocalDateTime.ofInstant(instant, ZoneId.systemDefault()).getYear();
            return new MovieSearchGetVm(item.getId(), item.getTitle(), year, item.getBackdropPath());
        }).limit(3).collect(Collectors.toList());
    }

    public Page<MovieSearchGetVm> getAllMovieByTitle(String input, Pageable pageable) {
        String sanitized = input.replaceAll("[\\*\\\"\\?\\~]", "").trim();

        if (sanitized.isEmpty()) return Page.empty();

        return mediaContentSearchRepository.findAllByTitleContaining(sanitized, pageable).map(item -> {
                    Instant instant = Instant.ofEpochMilli(item.getReleaseDate());
                    Long year = (long) LocalDateTime.ofInstant(instant, ZoneId.systemDefault()).getYear();
                    return new MovieSearchGetVm(item.getId(), item.getTitle(), year, item.getBackdropPath());
                }
        );
    }
}
