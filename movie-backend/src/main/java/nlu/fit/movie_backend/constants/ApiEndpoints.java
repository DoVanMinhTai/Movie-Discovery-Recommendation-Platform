package nlu.fit.movie_backend.constants;

public interface ApiEndpoints {
    interface Admin {
        String BASE = "/admin";

        String STATISTICS = BASE + "/statistics";
        String USERS = BASE + "/user/users";
        String DELETE_USER = BASE + "/user/{id}";
        String MOVIES = BASE + "/movie/movies";
        String ADD_MOVIE = BASE + "/movie/movies";
        String UPDATE_MOVIE = BASE + "/movie/movies";
        String DELETE_MOVIE = BASE + "/movie/movies" + "/{id}";
        String AI_STATUS = BASE + "/ai/movies";
        String RETRAIN_AI = BASE + "/ai/update-recommendations";
        String CHECK_DUPLICATE = BASE + "/movie/check-duplicate";
    }

    interface Auth {
        String BASE = "/auth";

        String REGISTER = BASE + "/register";
        String LOGIN = BASE + "/login";
        String PROFILE = BASE + "/profile";
        String EXIST_EMAIL = BASE + "/exist-email";
    }

    interface Chatbot {
        String BASE = "/chatbot";

        String CHATBOT = BASE + "/message";
        String HISTORY = BASE + "/history";
    }

    interface Category {
        String BASE = "/category";

        String ALL = BASE + "/genres";
    }

    interface MediaContent {
        String BASE = "/mediacontent";

        String GET_BY_ID = BASE + "/{movieId}";
    }

    interface Movie {
        String BASE = "/movie";

        String MOVIES = BASE + "/movies";
        String LATEST_MOVIES = BASE + "/latest";
        String TRENDING = BASE + "/trending";
        String HERO = BASE + "/hero";
        String TOP10 = BASE + "/top10";
        String MOVIE_GENRES = BASE + "/preferredGenres";
        String FILTER = BASE + "/filter";
    }

    interface Recommendation {
        String BASE = "/recommendation";

        String GET_CF_USERID = BASE + "/cf/user/{userId}";
        String GET_CF_SIMILAR_BY_MOVIE_ID = BASE + "/cf/similar/{movieId}";

        String GET_CBF_SEARCH = BASE + "/cbf/search";
        String GET_CBF_SIMILAR_BY_MOVIE_ID = BASE + "/cbf/similar/{movieId}";
        String GET_HYBRID_RECOMMENDATION = BASE + "/hybrid/{userId}";

    }

    interface Search {
        String BASE = "/search";
        String SUGGESTION = BASE + "/suggestion";
        String ALL = BASE + "/all";
    }

    interface UserInteraction {
        String BASE = "/user-interaction";

        String GET_ALL_FAVORITE = BASE + "/favorites";
        String ADD_MOVIE_FAVORITE = BASE + "/favorites/add";
        String DELETE_MOVIE_FAVORITE = BASE + "/favorites/delete/{movieId}";

        String ADD_RATE = BASE + "/rate";
        String GET_RATE = BASE + "/rate/{mediaContentId}";

        String ONBOARDING = BASE + "/onboarding";

        String ADD_WATCH_HISTORY = BASE + "/addWatchHistory";
        String EXISTS_WATCH_HISTORY = BASE + "/checkWatchHistory/{mediaContentId}";

    }

}
