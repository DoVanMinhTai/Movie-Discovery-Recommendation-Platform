package nlu.fit.movie_backend.mapper.impl.media;

import lombok.RequiredArgsConstructor;
import nlu.fit.movie_backend.mapper.MediaMapper;
import nlu.fit.movie_backend.model.MediaContent;
import nlu.fit.movie_backend.viewmodel.movie.MediaContentGetVm;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
@RequiredArgsConstructor
public class MediaMapperFactory {
    private final List<MediaMapper> mappers;

    public MediaContentGetVm getVm(MediaContent mediaContent) {
        return mappers.stream()
                .filter(m -> m.supports(mediaContent))
                .findFirst()
                .map(m -> m.map(mediaContent))
                .orElseThrow(() -> new IllegalArgumentException("This type of media is not supported"));
    }
}
