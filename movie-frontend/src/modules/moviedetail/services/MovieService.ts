import apiClientService, { type PageAbleResponse } from "../../../common/services/ApiClientService";
import type { MovieThumbnailVm } from "../model/MovieThumbnailVm";

export async function getMovieDetailById(movieId: number) : Promise<PageAbleResponse> {
    const response = await apiClientService.get(process.env.REACT_APP_API_BASE_URL + `/movie/${Number(movieId)}`);
    return response.data;
}

export async function getMovieSimilarById(movieId: number) : Promise<MovieThumbnailVm[]> {
    const response = await apiClientService.get(process.env.REACT_APP_API_BASE_URL + `/recommendation/similar/${movieId}`);
    return response.data;
}