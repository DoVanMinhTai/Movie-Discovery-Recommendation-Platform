package nlu.fit.movie_backend.service;

import jakarta.transaction.Transactional;
import lombok.AllArgsConstructor;
import nlu.fit.movie_backend.model.*;
import nlu.fit.movie_backend.repository.jpa.*;
import nlu.fit.movie_backend.viewmodel.movie.MovieFavoritesGetVm;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Set;

@Service
@AllArgsConstructor
public class UserService {
    private final UserRepository userRepository;
    private final FavoriteRepository favoriteRepository;
    private final MediaContentRepository mediaContentRepository;
    private final GenreRepository genreRepository;
    private final JWTService jwtService;

    public List<MovieFavoritesGetVm> getAllMovieFavorites(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found with id: " + userId));

        List<Favorite> favorites = favoriteRepository.findAllByUserId(user.getId(), Pageable.unpaged());

        return favorites.stream()
                .map(item -> new MovieFavoritesGetVm(
                        item.getMediaContent().getId(),
                        item.getMediaContent().getTitle(),
                        item.getMediaContent().getBackdropPath()
                ))
                .toList();
    }

    public Void addFavorite(Long userId, Long mediaContentId) {
         boolean exists = favoriteRepository.existsByUserIdAndMediaContentId(userId, mediaContentId);
         if (exists) return null;

        MediaContent mediaContent = mediaContentRepository.findById(mediaContentId).orElseThrow(
                () -> new RuntimeException("MediaContent not found")
        );

        Favorite favorite = new Favorite();
        favorite.setMediaContent(mediaContent);
        favorite.setUser(userRepository.findById(userId).orElseThrow(
                () -> new RuntimeException("User not found")
        ));
        favoriteRepository.save(favorite);
        return null;
    }

    @Transactional
    public Void deleteFavorite(Long userId, Long movieId) {
        Favorite favorite = favoriteRepository.findByUserIdAndMediaContent_Id(userId, movieId);

        if (favorite != null) {
            favoriteRepository.delete(favorite);
        } else {
            throw new RuntimeException("Không tìm thấy phim này trong danh sách yêu thích");
        }
        return null;
    }

    public User deleteUser(Long id) {
        User user = userRepository.findById(id).orElseThrow(
                () -> new RuntimeException("User not found")
        );
        user.setDeleted(true);
        return userRepository.save(user);
    }

    @Transactional
    public String processOnBoarding(String email, List<Long> genreIds) {
        User user = userRepository.findByEmail(email).orElseThrow(()  -> new RuntimeException("User not found"));

        Set<Genre> genres = genreRepository.findAllByIdIn(genreIds);

        user.setPreferredGenres(genres);
        User updatedUser = userRepository.save(user);

        return jwtService.generateJWTToken(updatedUser);
    }
}
