import apiClientService from "../../../common/services/ApiClientService";

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function getMyProfile() {
    const response = await apiClientService.get(BASE_URL + "/auth/profile");
    return response.data; 
}