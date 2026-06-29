package nlu.fit.movie_backend.service;

import lombok.RequiredArgsConstructor;
import nlu.fit.movie_backend.model.User;
import nlu.fit.movie_backend.repository.jpa.*;
import nlu.fit.movie_backend.viewmodel.admin.*;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class AdminService {

    private final MediaContentRepository mediaContentRepository;
    private final UserRepository userRepository;
    private final RateRepository rateRepository;
    private final ModelRegistryRepository modelRegistryRepository;
    private final TrainingJobRepository trainingJobRepository;
    private final WatchHistoryRepository watchHistoryRepository;
    private final MovieRepository movieRepository;

    public AdminStatsResponse getStatistics(LocalDate from, LocalDate to) {
        if (from == null) {
            from = LocalDate.now().minusDays(30);
        }
        if (to == null) {
            to = LocalDate.now();
        }

        long totalUsers = userRepository.count();
        long totalMedia = mediaContentRepository.count();

        LocalDateTime startRange = from.atStartOfDay();
        LocalDateTime endRange = to.plusDays(1).atStartOfDay();

        long totalRatings = rateRepository.countByCreatedAtBetween(startRange, endRange);

        LocalDateTime todayStart = LocalDate.now().atStartOfDay();
        LocalDateTime todayEnd = LocalDate.now().plusDays(1).atStartOfDay();
        long viewsToday = watchHistoryRepository.countByWatchedAtBetween(todayStart, todayEnd);

        List<MovieResponse> recentMovies = mediaContentRepository.findTop5ByOrderByIdDesc()
                .stream()
                .map(m -> new MovieResponse(m.getId(), m.getTitle(), m.getReleaseDate().getYear()))
                .toList();

        List<Object[]> rawDailyViews = watchHistoryRepository.countDailyViewsBetween(startRange, endRange);
        List<DailyViewDto> dailyViews = rawDailyViews.stream()
                .map(row -> new DailyViewDto(row[0].toString(), ((Number) row[1]).longValue()))
                .toList();

        return new AdminStatsResponse(
                totalUsers,
                totalMedia,
                totalRatings,
                viewsToday,
                recentMovies,
                dailyViews
        );
    }

    public boolean checkDuplicate(String title, int year, Long excludeId) {
        if (excludeId != null) {
            return movieRepository.existsByTitleAndYearExcluding(title, year, excludeId);
        } else {
            return movieRepository.existsByTitleAndYear(title, year);
        }
    }

    public List<UserResponse> getAllUsers() {
        Pageable pageable = PageRequest.of(0, 10);
        Page<User> users = userRepository.findAll(pageable);
        return users.stream().map(user -> new UserResponse(user.getId(), user.getEmail(), user.getEmail())).toList();
    }

    public AiStatusResponse getAiStatus() {
        var activeModelOpt = modelRegistryRepository.findByIsActiveTrue();
        ActiveModelDto activeModel = activeModelOpt.map(m -> new ActiveModelDto(
                m.getModelName(), m.getVersion(), m.getRmse(),
                m.getMae(), m.getF1Score(), m.getModelPath()
        )).orElse(null);

        List<JobLogDto> recentJobs = trainingJobRepository.findTop10ByOrderByCreatedAtDesc()
                .stream()
                .map(j -> new JobLogDto(j.getId(), j.getJobStatus(),
                        j.getCreatedAt() != null ? j.getCreatedAt().toString() : "",
                        j.getErrorMessage(), j.getContentBasedTime(),j.getCollaboratingTime()))
                .toList();

        JobLogDto currentJob = recentJobs.stream()
                .filter(j -> "PENDING".equals(j.status()))
                .findFirst()
                .orElse(null);

        return new AiStatusResponse(activeModel, recentJobs, currentJob);
    }


}
