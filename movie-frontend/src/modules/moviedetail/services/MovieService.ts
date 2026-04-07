import apiClientService from "../../../common/services/ApiClientService";
import type { MovieThumbnailVm } from "../model/MovieThumbnailVm";
import type { RatingPostVm } from "../model/RatingPostVm";

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function getMediaContentById(movieId: number) : Promise<any> {
    const response = await apiClientService.get(BASE_URL + `/movie/${Number(movieId)}`);
    return response.data;
}

export async function getMovieSimilarById(movieId: number) : Promise<MovieThumbnailVm[]> {
    const response = await apiClientService.get(BASE_URL + `/recommendation/similar/${movieId}`);
    return response.data;
}

export async function canRateMovie(movieId: number) : Promise<boolean> {
    const response = await apiClientService.get(BASE_URL + `/user/api/checkWatchHistory/${movieId}`);
    return response.data;
}

export async function rateMovie(ratingPostVm: RatingPostVm) : Promise<boolean> {
    const response = await apiClientService.post(BASE_URL + `/user/api/rateMovie`, ratingPostVm);
    return response.data;
}
