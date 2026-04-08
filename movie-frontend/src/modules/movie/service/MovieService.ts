import { API_ENDPOINTS } from "../../../common/constants/ApiEndpoints";
import apiClientService from "../../../common/services/ApiClientService";
import type { MediaContentGetVm } from "../model/MediaContentGetVm";
import type { MovieThumbnailGetVm } from "../model/MovieThumbnailGetVm";
import type { RatingPostVm } from "../model/RatingPostVm";

export async function getMediaContentById(movieId: number): Promise<MediaContentGetVm> {
    const response = await apiClientService.get(API_ENDPOINTS.MEDIA_CONTENT.GET_BY_ID(movieId));
    return response.data;
}

export async function getMovieSimilarById(movieId: number): Promise<MovieThumbnailGetVm[]> {
    const response = await apiClientService.get(API_ENDPOINTS.MOVIE.SIMILAR(movieId));
    return response.data;
}

export async function canRateMovie(movieId: number): Promise<boolean> {
    const response = await apiClientService.get(API_ENDPOINTS.USER.CAN_RATE(movieId));
    return response.data;
}

export async function rateMovie(ratingPostVm: RatingPostVm): Promise<boolean> {
    const response = await apiClientService.post(API_ENDPOINTS.USER.RATE, ratingPostVm);
    return response.data;
}
