import apiClientService from "../../../common/services/ApiClientService"

const BASE_URL = import.meta.env.VITE_API_BASE_URL + "/movie/";

export async function getMovieByType(type: string) {
    const response = await apiClientService.get(BASE_URL, {
        params: { type: type }
    })

    return response.data;
}

export async function getAllGenres() {
    const response = await apiClientService.get(BASE_URL + "movies/genres");
    console.log("Genres response:", response);
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
    const response = await apiClientService.get(BASE_URL + "movies/", {
        params: params
    });
    return response.data;
}