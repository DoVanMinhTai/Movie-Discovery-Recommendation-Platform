package nlu.fit.movie_backend.mapper.impl.movie;

import org.springframework.data.domain.Sort;

public enum MovieSortStrategy {
    NEWEST("releaseDate", Sort.Direction.DESC),
    OLDEST("releaseDate", Sort.Direction.ASC),
    POPULARITY("popularity", Sort.Direction.DESC),
    RATING("voteAverage", Sort.Direction.DESC),
    TITLE_AZ("title", Sort.Direction.ASC);

    private final String databaseField;

    private final Sort.Direction direction;


    MovieSortStrategy(String databaseField, Sort.Direction direction) {
        this.databaseField = databaseField;
        this.direction = direction;
    }

    public static MovieSortStrategy fromString(String value) {
        try {
            return MovieSortStrategy.valueOf(value);
        } catch (IllegalArgumentException | NullPointerException e) {
            return NEWEST;
        }
    }

    public Sort getSortConfig() {
        return Sort.by(this.direction, this.databaseField);
    }
}
