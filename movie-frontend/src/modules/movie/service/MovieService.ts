import { API_ENDPOINTS } from "../../../constants/ApiEndpoints";
import apiClientService from "../../../common/services/ApiClientService";
import type { MediaContentGetVm } from "../model/MediaContentGetVm";
import type { MovieThumbnailGetVm } from "../model/MovieThumbnailGetVm";
import type { RatingPostVm } from "../model/RatingPostVm";

export async function getMediaContentById(movieId: number): Promise<MediaContentGetVm> {
    const response = await apiClientService.get(API_ENDPOINTS.MEDIA_CONTENT.GET_BY_ID(movieId));
    return response;
}

export async function getMovieSimilarById(movieId: number): Promise<MovieThumbnailGetVm[]> {
    const response = await apiClientService.get(API_ENDPOINTS.RECOMMENDATION.CBF.SIMILAR(movieId));
    return response;
}

export async function canRateMovie(movieId: number): Promise<boolean> {
    const response = await apiClientService.get(API_ENDPOINTS.USER.GET_RATE_BY_MOVIE_ID(movieId));
    return response;
}

export async function getRatingByMovieId(movieId: number): Promise<any> {
    const response = await apiClientService.get(API_ENDPOINTS.USER.GET_RATE_BY_MOVIE_ID(movieId));
    return response;
}

export async function addRateMovie(ratingPostVm: RatingPostVm): Promise<boolean> {
    const response = await apiClientService.post(API_ENDPOINTS.USER.ADD_RATE, ratingPostVm);
    return response;
}

export async function addToWatchHistory(movieId: number): Promise<void> {
    await apiClientService.post(API_ENDPOINTS.USER.ADD_WATCH_HISTORY, { movieId: movieId });
}

export async function getCollaborativeFiltering(userId: number): Promise<MovieThumbnailGetVm[]> {
    const response = await apiClientService.get(API_ENDPOINTS.RECOMMENDATION.CF.USER(userId));
    return response;
}
