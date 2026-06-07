import { API_ENDPOINTS } from "../../../constants/ApiEndpoints";
import apiClientService from "../../../common/services/ApiClientService";

export async function getMovieSuggestionByTitle(query: string) {
    const response = await apiClientService.get(API_ENDPOINTS.SEARCH.SUGGEST, {
        params: { q: query }
    });
    console.log(response);
    return response;
}

export async function getAllMovieByTitle(query: string) {
    const response = await apiClientService.get(API_ENDPOINTS.SEARCH.ALL, {
        params: { q: query, pageAblesize: 20 },
    });
    return response;
}


