package nlu.fit.movie_backend.model;

import jakarta.persistence.*;
import lombok.*;
import nlu.fit.movie_backend.model.enumeration.ROLE;

import java.util.List;
import java.util.Set;

@Entity()
@Table(name = "users")
@Getter
@Setter
@ToString
@AllArgsConstructor
@NoArgsConstructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String userName;

    private String password;

    private String email;

    @Enumerated(EnumType.STRING)
    @Column(length = 20)
    private ROLE role = ROLE.USER;

    private String fullName;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL)
    private List<Rating> ratings;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL)
    private List<Favorite> favorites;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL)
    private List<WatchHistory> watchHistory;

    @ManyToMany
    @JoinTable(
            name = "user_preferred_genres",
            joinColumns = @JoinColumn(name = "user_id"),
            inverseJoinColumns = @JoinColumn(name = "genre_id")
    )
    private Set<Genre> preferredGenres;

    private boolean isDeleted;

}
