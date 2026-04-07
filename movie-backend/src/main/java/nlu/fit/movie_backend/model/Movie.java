package nlu.fit.movie_backend.model;

import jakarta.persistence.*;
import lombok.*;

@Table(name = "movies")
@Entity()
@Getter
@Setter
@ToString
@AllArgsConstructor
@NoArgsConstructor
@DiscriminatorValue(value = "MOVIE")
public class Movie extends MediaContent {

    @Column(name = "runtime")
    private Integer runtime;

    @Column(name = "trailer_key")
    private String trailerKey;

    @Column(name = "video_url")
    private String videoUrl;
}
