package nlu.fit.movie_backend.viewmodel.recommendation;

public record MovieSimilarCBFItem(
        String movie_id,
        String title,
        String genres,
        Double score
) {
}
