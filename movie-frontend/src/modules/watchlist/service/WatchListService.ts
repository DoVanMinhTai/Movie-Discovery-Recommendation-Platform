import { API_ENDPOINTS } from "../../../common/constants/ApiEndpoints";

export async function getWatchList(): Promise<any> {
    const response = await fetch(API_ENDPOINTS.USER.GET_FAVORITES, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem("token")}` }
    });
    if (!response.ok) throw new Error("Không thể tải danh sách");
    return response.json();
}

export async function removeFromWatchList(movieId: number): Promise<void> {
    const response = await fetch(API_ENDPOINTS.USER.REMOVE_FAVORITE(movieId), {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem("token")}` }
    });
    if (!response.ok) throw new Error("Không thể xóa phim");
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
    if (!response.ok) throw new Error("Không thể thêm phim");
}