package nlu.fit.movie_backend.viewmodel.admin;

import java.util.List;

public record AdminStatsResponse(
        long totalUsers,
        long totalMedia,
        long totalRatings,
        long viewsToday,
        List<MovieResponse> recentMovies,
        List<DailyViewDto> dailyViews
) {
}
