package nlu.fit.movie_backend.service;

import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import nlu.fit.movie_backend.model.MediaContent;
import nlu.fit.movie_backend.model.Rating;
import nlu.fit.movie_backend.model.User;
import nlu.fit.movie_backend.model.WatchHistory;
import nlu.fit.movie_backend.repository.jpa.*;
import nlu.fit.movie_backend.viewmodel.rate.RatingPostVm;

import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class RateService {
    private final RateRepository rateRepository;
    private final UserRepository userRepository;
    private final MediaContentRepository mediaContentRepository;
    private final WatchHistoryRepository watchHistoryRepository;

    @Transactional
    public Rating rateMovie(Long userId, RatingPostVm ratingRequest) {
        Rating rating = rateRepository.findByUserIdAndMediaContentId(userId, ratingRequest.movieId())
                .orElse(new Rating());

        MediaContent mediaContent = mediaContentRepository.findById(ratingRequest.movieId())
                .orElseThrow(() -> new RuntimeException("Phim không tồn tại"));

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("Người dùng không tồn tại"));

        rating.setScore(ratingRequest.score());
        rating.setComment(ratingRequest.comment());
        rating.setMediaContent(mediaContent);
        rating.setUser(user);
        
        return rateRepository.save(rating);
    }

    public Boolean checkWatchHistory(Long userId, Long mediaContentId) {
        return watchHistoryRepository.existsByUserIdAndMediaContentId(userId, mediaContentId);
    }

    public Rating getRating(Long userId, Long mediaContentId) {
        return rateRepository.findByUserIdAndMediaContentId(userId, mediaContentId).orElse(null);
    }

    @Transactional
    public void addToWatchHistory(Long userId, Long mediaContentId) {
        if (!checkWatchHistory(userId, mediaContentId)) {
            User user = userRepository.findById(userId)
                    .orElseThrow(() -> new RuntimeException("Người dùng không tồn tại"));
            MediaContent mediaContent = mediaContentRepository.findById(mediaContentId)
                    .orElseThrow(() -> new RuntimeException("Phim không tồn tại"));

            WatchHistory watchHistory = new WatchHistory();
            watchHistory.setUser(user);
            watchHistory.setMediaContent(mediaContent);
            watchHistory.setWatchedAt(LocalDateTime.now());
            watchHistoryRepository.save(watchHistory);
        }
    }
}
