import { API_ENDPOINTS } from "../../../common/constants/ApiEndpoints";
import apiClientService from "../../../common/services/ApiClientService"

export async function getAllGenre() {
    const response = await apiClientService.get(API_ENDPOINTS.CATEGORY.GET_ALL);
    return response.data;
}

export async function getMoviesFilter({ sortBy, genre, page }: { sortBy: string; genre: string; page: number }) {
    const params: any = {
        sortBy: sortBy,
        page: page,
        size: 10
    };
    if (genre) {
        params.genre = genre;
    }
    const response = await apiClientService.get(API_ENDPOINTS.MOVIE.FILTER, {
        params: params
    });
    return response.data;
}