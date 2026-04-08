package nlu.fit.movie_backend.mapper;

import nlu.fit.movie_backend.model.MediaContent;
import nlu.fit.movie_backend.viewmodel.movie.MediaContentGetVm;

public interface MediaMapper {
    boolean supports(MediaContent mediaContent);
    MediaContentGetVm map(MediaContent mediaContent);
}
