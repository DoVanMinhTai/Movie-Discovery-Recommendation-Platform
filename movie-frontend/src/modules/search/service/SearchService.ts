import { API_ENDPOINTS } from "../../../common/constants/ApiEndpoints";
import apiClientService from "../../../common/services/ApiClientService";

export async function getMovieSuggestionByTitle(query: string) {
    const response = await apiClientService.get(API_ENDPOINTS.SEARCH.SUGGEST, {
        params: { q: query }
    });
    return response.data;
}

export async function getAllMovieByTitle(query: string) {
    const response = await apiClientService.get(API_ENDPOINTS.SEARCH.ALL, {
        params: { q: query, pageAblesize: 20 },
    });
    return response.data;
}


