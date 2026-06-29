package nlu.fit.movie_backend.viewmodel.recommendation;

import java.util.List;

public record MovieSimilarCBFResponse(
        Long movie_id,
        String movie_title,
        List<MovieSimilarCBFItem> recommendations
) {
}
