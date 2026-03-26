import apiClientService from "../../../common/services/ApiClientService";

export async function getMovieSuggestionByTitle(query: string) {
    const response = await apiClientService.get(process.env.REACT_APP_API_BASE_URL + "/search/suggest", {
        params: { q: query }
    });
    return response.data;
}

export async function getAllMovieByTitle(query: string) {
    const response = await apiClientService.get(process.env.REACT_APP_API_BASE_URL + "/search/all", {
        params: { q: query, pageAblesize: 20 },
    });
    return response.data;
}


