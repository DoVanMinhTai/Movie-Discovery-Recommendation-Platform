package nlu.fit.movie_backend.viewmodel.rate;

public record RatingPostVm(
        Double score, String comment, Long movieId
) {
}
