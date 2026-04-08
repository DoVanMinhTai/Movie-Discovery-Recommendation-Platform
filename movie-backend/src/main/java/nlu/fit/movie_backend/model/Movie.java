package nlu.fit.movie_backend.model;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.SQLDelete;
import org.hibernate.annotations.Where;

@Table(name = "movies")
@Entity()
@Getter
@Setter
@ToString
@AllArgsConstructor
@NoArgsConstructor
@DiscriminatorValue(value = "MOVIE")
@SQLDelete(sql = "UPDATE movie SET isDeleted = true WHERE id = ?")
@Where(clause = "deleted = false")
public class Movie extends MediaContent {

    @Column(name = "runtime")
    private Integer runtime;

    @Column(name = "trailer_key")
    private String trailerKey;

    @Column(name = "video_url")
    private String videoUrl;
}
