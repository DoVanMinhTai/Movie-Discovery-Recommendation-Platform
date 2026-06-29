package nlu.fit.movie_backend.controller;

import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.constants.ApiEndpoints;
import nlu.fit.movie_backend.model.Genre;
import nlu.fit.movie_backend.model.enumeration.CONTENTTYPE;
import nlu.fit.movie_backend.service.JWTService;
import nlu.fit.movie_backend.service.MovieService;
import nlu.fit.movie_backend.viewmodel.ApiResponse;
import nlu.fit.movie_backend.viewmodel.movie.MediaContentGetVm;
import nlu.fit.movie_backend.viewmodel.movie.MovieHeroGetVm;
import nlu.fit.movie_backend.viewmodel.movie.MovieThumbnailGetVm;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@AllArgsConstructor
@CrossOrigin(origins = "${app.cors.allowed-origins}")
public class MediaContentController {
    private final MovieService movieService;

    @GetMapping(ApiEndpoints.MediaContent.GET_BY_ID)
    public ResponseEntity<ApiResponse<MediaContentGetVm>> getMediaContentById(@PathVariable Long movieId) {
        return ResponseEntity.ok(
                ApiResponse.<MediaContentGetVm>builder().result(movieService.getMediaContentById(movieId)).build()
        );
    }

}
