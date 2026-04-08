package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.model.Genre;
import nlu.fit.movie_backend.model.enumeration.CONTENTTYPE;
import nlu.fit.movie_backend.service.JWTService;
import nlu.fit.movie_backend.service.MovieService;
import nlu.fit.movie_backend.viewmodel.movie.MediaContentGetVm;
import nlu.fit.movie_backend.viewmodel.movie.MovieHeroGetVm;
import nlu.fit.movie_backend.viewmodel.movie.MovieThumbnailGetVm;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/mediacontent")
@AllArgsConstructor
@CrossOrigin(origins = "*")
public class MediaContentController {
    private final MovieService movieService;

    @GetMapping("/{movieId}")
    public ResponseEntity<MediaContentGetVm> getMediaContentById(@PathVariable Long movieId) {
        return ResponseEntity.ok(movieService.getMediaContentById(movieId));
    }

}
