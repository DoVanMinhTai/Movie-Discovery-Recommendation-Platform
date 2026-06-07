import apiClientService from "../../../common/services/ApiClientService";
import { API_ENDPOINTS } from "../../../constants/ApiEndpoints";

export async function getWatchList(): Promise<any> {
    const response = await apiClientService.get(API_ENDPOINTS.USER.GET_FAVORITES);
    return response;
}

export async function removeFromWatchList(movieId: number): Promise<void> {
    const response = await apiClientService.delete(API_ENDPOINTS.USER.REMOVE_FAVORITE(movieId));
    return response;
}

export async function addToWatchList(movieId: number): Promise<void> {
    const response = await fetch(API_ENDPOINTS.USER.ADD_FAVORITE, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify(movieId)
    });
    console.log("Response status:", response.status);
    if (!response.ok) throw new Error("Không thể thêm phim");
}