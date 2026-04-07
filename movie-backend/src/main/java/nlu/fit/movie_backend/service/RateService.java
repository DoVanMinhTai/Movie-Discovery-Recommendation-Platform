package nlu.fit.movie_backend.service;

import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import nlu.fit.movie_backend.model.MediaContent;
import nlu.fit.movie_backend.model.Rating;
import nlu.fit.movie_backend.model.User;
import nlu.fit.movie_backend.repository.jpa.*;
import nlu.fit.movie_backend.viewmodel.rate.RatingPostVm;

import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class RateService {
    private final RateRepository rateRepository;
    private final UserRepository userRepository;
    private final MediaContentRepository mediaContentRepository;
    private final WatchHistoryRepository watchHistoryRepository;

    @Transactional
    public Rating rateMovie(Long userId, RatingPostVm ratingRequest) {
        boolean hasWatch = checkWatchHistory(userId, ratingRequest.movieId());
        if (hasWatch) {
            throw new RuntimeException("Bạn phải xem phim trước khi có thể đánh giá hoặc bình luận!");
        }

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
}
