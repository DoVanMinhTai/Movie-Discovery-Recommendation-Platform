package nlu.fit.movie_backend.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import nlu.fit.movie_backend.model.Genre;
import nlu.fit.movie_backend.repository.jpa.GenreRepository;
import nlu.fit.movie_backend.viewmodel.movie.*;
import org.springframework.stereotype.Service;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class GenreService {
    private final GenreRepository genreRepository;

    public List<Genre> getAllGenres() {
        return genreRepository.findAll();
    }

    public List<Genre> findAllById(List<Long> genreIds) {
        return genreRepository.findAllById(genreIds);
    }
}
