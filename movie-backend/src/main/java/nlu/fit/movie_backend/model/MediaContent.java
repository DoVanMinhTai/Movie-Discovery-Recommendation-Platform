package nlu.fit.movie_backend.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Entity()
@Table(name = "mediacontent")
@Getter
@Setter
@Inheritance(strategy = InheritanceType.JOINED)
@DiscriminatorColumn(name = "dtype", discriminatorType = DiscriminatorType.STRING)
public abstract class MediaContent {
    @Id
    @Column(name = "movieId")
    private Long id;

    @Column(name = "tmdbId", unique = true)
    private Long tmDBId;

    @Column(name = "title")
    private String title;

    @Column(name = "original_title")
    private String originalTitle;

    @ManyToMany(cascade = {CascadeType.PERSIST, CascadeType.MERGE}, fetch = FetchType.LAZY)
    @JoinTable(name = "mediacontent_genres", joinColumns = @JoinColumn(name = "mediacontent_id"), inverseJoinColumns = @JoinColumn(name = "genre_id"))
    private List<Genre> genres;

    @Column(name = "overview", columnDefinition = "TEXT")
    private String overview;

    @Column(name = "release_date")
    private LocalDateTime releaseDate;

    @Column(name = "poster_path")
    private String posterPath;

    @Column(name = "backdrop_path")
    private String backdropPath;

    @Column(name = "tmdb_vote")
    private Double voteAverage;

    @Column(name = "vote_count")
    private int voteCount;

    @Column(name = "popularity")
    private Double popularity;

    private Long movieLensId;

    private String originalLanguage;

    @OneToMany(mappedBy = "mediaContent", cascade = CascadeType.ALL)
    private List<Rating> rating;

    @OneToMany(mappedBy = "mediaContent", cascade = CascadeType.ALL)
    private List<Favorite> favorite;

    @OneToMany(mappedBy = "mediaContent", cascade = CascadeType.ALL)
    private List<WatchHistory> watchHistory;

    @Column(nullable = false, columnDefinition = "boolean default false")
    private boolean isDeleted = false;

    @Column(insertable = false, updatable = false)
    String dtype;

    @Column(name = "\"cast\"", columnDefinition = "TEXT")
    String cast;

    @Column(columnDefinition = "TEXT")
    String director;

}
