import apiClientService from "../../../common/services/ApiClientService";

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function getMovieSuggestionByTitle(query: string) {
    const response = await apiClientService.get(BASE_URL + "/search/suggest", {
        params: { q: query }
    });
    return response.data;
}

export async function getAllMovieByTitle(query: string) {
    const response = await apiClientService.get(BASE_URL + "/search/all", {
        params: { q: query, pageAblesize: 20 },
    });
    return response.data;
}


