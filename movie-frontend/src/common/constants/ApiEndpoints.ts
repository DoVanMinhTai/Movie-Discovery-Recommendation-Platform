const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const API_ENDPOINTS = {
    ADMIN: {
        DASHBOARD: `${BASE_URL}/admin/dashboard`,
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
        TRENDING: `${BASE_URL}/movie/movies/trending?limit=10`,
        HERO_MOVIE: `${BASE_URL}/movie/movies/hero`,
        PREFERRED_GENRES: `${BASE_URL}/movie/movies/preferredGenres?limit=10`,
        TOP10: `${BASE_URL}/movie/movies/top10`,
    },
    MOVIE: {
        GENRES: `${BASE_URL}/movie/movies/genres`,
        FILTER: `${BASE_URL}/movie/movies/`,
        SIMILAR: (movieId: number) => `${BASE_URL}/recommendation/similar/${movieId}`
    },
    MEDIA_CONTENT: {
        GET_BY_ID: (movieId: number) => `${BASE_URL}/mediacontent/${movieId}`,
    },
    USER: {
        CAN_RATE: (movieId: number) => `${BASE_URL}/user/api/checkWatchHistory/${movieId}`,
        RATE: `${BASE_URL}/user/api/rateMovie`,
        GET_FAVORITES: `${BASE_URL}/user/api/getAllFavorites`,
        ADD_FAVORITE: `${BASE_URL}/user/api/favorites/add`,
        REMOVE_FAVORITE: (movieId: number) => `${BASE_URL}/user/api/favorites/${movieId}`,
    },
    SEARCH: {
        SUGGEST: `${BASE_URL}/search/suggest`,
        ALL: `${BASE_URL}/search/all`,
    }

} as const;