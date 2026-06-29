const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const API_ENDPOINTS = {
    ADMIN: {
        DASHBOARD: `${BASE_URL}/admin/statistics`,
        AI_STATUS: `${BASE_URL}/admin/ai-status`,
        RETRAIN_AI: `${BASE_URL}/admin/retrain-ai`,
        UPDATE_RECOMMENDATIONS: `${BASE_URL}/admin/update-recommendations`,
    },
    AUTH: {
        REGISTER: `${BASE_URL}/auth/register`,
        LOGIN: `${BASE_URL}/auth/login`,
        EXIST_EMAIL: `${BASE_URL}/auth/exist-email`,
        GET_PROFILE: `${BASE_URL}/auth/profile`,
    },
    CATEGORY: {
        GET_ALL: `${BASE_URL}/category/genres`,
    },
    CHATBOT: {
        MESSAGE: `${BASE_URL}/chatbot/message`,
    },
    HOMEPAGE: {
        TRENDING: `${BASE_URL}/movie/trending?limit=10`,
        HERO_MOVIE: `${BASE_URL}/movie/hero`,
        PREFERRED_GENRES: `${BASE_URL}/movie/preferredGenres?limit=10`,
        TOP10: `${BASE_URL}/movie/top10`,
    },
    MOVIE: {
        GENRES: `${BASE_URL}/category/genres`,
        FILTER: `${BASE_URL}/movie/filter`,
    },
    MEDIA_CONTENT: {
        GET_BY_ID: (movieId: number) => `${BASE_URL}/mediacontent/${movieId}`,
    },
    USER: {
        GET_RATE_BY_MOVIE_ID: (movieId: number) => `${BASE_URL}/user-interaction/rate/${movieId}`,
        ADD_RATE: `${BASE_URL}/user-interaction/rate`,
        
        GET_FAVORITES: `${BASE_URL}/user-interaction/favorites`,
        ADD_FAVORITE: `${BASE_URL}/user-interaction/favorites/add`,
        REMOVE_FAVORITE: (movieId: number) => `${BASE_URL}/user-interaction/favorites/delete/${movieId}`,
        
        ADD_WATCH_HISTORY: `${BASE_URL}/user-interaction/addWatchHistory`,
        EXISTS_WATCH_HISTORY: (movieId: number) => `${BASE_URL}/user-interaction/checkWatchHistory/${movieId}`,
    },
    SEARCH: {
        SUGGEST: `${BASE_URL}/search/suggestion`,
        ALL: `${BASE_URL}/search/all`,
    },
    ONBOARDING: {
        POST: `${BASE_URL}/user-interaction/onboarding`,
    },
    RECOMMENDATION: {
        CF: {
            UPDATE_RECOMMENDATIONS: `${BASE_URL}/recommendation/cf/update-recommendations`,
            USER: (userId: number) => `${BASE_URL}/recommendation/cf/user/${userId}`,
            SIMILAR: (movieId: number) => `${BASE_URL}/recommendation/cf/similar/${movieId}`,
        },
        CBF: {
            SEARCH: `${BASE_URL}/recommendation/cbf/search`,
            SIMILAR: (movieId: number) => `${BASE_URL}/recommendation/cbf/similar/${movieId}`,
        }
    }
} as const;
