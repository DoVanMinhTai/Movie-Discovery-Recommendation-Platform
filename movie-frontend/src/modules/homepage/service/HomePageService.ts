import apiClientService from "../../../common/services/ApiClientService"
import type { ContentType } from "../model/enum/ContentType";

const baseURL = process.env.REACT_APP_API_BASE_URL;

export async function getTop10(contentType: ContentType, limit: number = 10) {
    const response = await apiClientService.get(`${baseURL}/movie/movies/top10?contenttype=${contentType}&limit=${limit}`);
    return response.data;
}

export async function getContinueWatching() {
    const response = await apiClientService.get(`${baseURL}/homepage/2`);
    return response.data;
}

export async function getTrending() {
    const response = await apiClientService.get(`${baseURL}/movie/movies/trending?limit=10`);
    return response.data;
}

export async function getHeroMovie() {
    const response = await apiClientService.get(`${baseURL}/movie/movies/hero`);
    return response.data;
}

export async function getMoviePreferredGenres(limit: number) {
    const response = (await apiClientService.get(
        `${baseURL}/movie/movies/preferredGenres?limit=${limit}`
    ));
    return response.data;
}