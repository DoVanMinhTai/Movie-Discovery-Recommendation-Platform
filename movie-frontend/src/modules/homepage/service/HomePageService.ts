import { API_ENDPOINTS } from "../../../common/constants/ApiEndpoints";
import apiClientService from "../../../common/services/ApiClientService"
import type { MovieThumbnailGetVm } from "../../movie/model/MovieThumbnailGetVm";
import type { MovieHeroGetVm } from "../model/MovieHeroGetVm";

export async function getTop10() : Promise<MovieThumbnailGetVm[]> {
    const response = await apiClientService.get(API_ENDPOINTS.HOMEPAGE.TOP10);
    return response.data;
}

export async function getTrending() : Promise<MovieThumbnailGetVm[]> {
    const response = await apiClientService.get(API_ENDPOINTS.HOMEPAGE.TRENDING);
    return response.data;
}

export async function getHeroMovie() : Promise<MovieHeroGetVm> {
    const response = await apiClientService.get(API_ENDPOINTS.HOMEPAGE.HERO_MOVIE);
    return response.data;
}

export async function getMoviePreferredGenres(limit: number) : Promise<Record<string, MovieThumbnailGetVm[]>> {
    const response = (await apiClientService.get(
        API_ENDPOINTS.HOMEPAGE.PREFERRED_GENRES.replace("{limit}", limit.toString())
    ));
    return response.data;
}