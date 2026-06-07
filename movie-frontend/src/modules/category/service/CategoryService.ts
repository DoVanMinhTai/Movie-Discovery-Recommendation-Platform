import { API_ENDPOINTS } from "../../../constants/ApiEndpoints";
import apiClientService from "../../../common/services/ApiClientService"

export async function getAllGenre() {
    const response = await apiClientService.get(API_ENDPOINTS.CATEGORY.GET_ALL);
    return response;
}

export async function getMoviesFilter({ sortBy, genre, dtype, page }: { sortBy: string; genre: string; dtype: string; page: number }) {
    const params: any = {
        sortBy: sortBy,
        page: page,
        size: 10
    };
    if (genre) {
        params.genre = genre;
    }
    if (dtype) {
        params.dtype = dtype;
    }
    const response = await apiClientService.get(API_ENDPOINTS.MOVIE.FILTER, {
        params: params
    });
    return response;
}