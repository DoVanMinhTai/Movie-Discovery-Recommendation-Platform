import apiClientService from "../../../common/services/ApiClientService";

export async function getMyProfile() {
    const response = await apiClientService.get(process.env.REACT_APP_API_BASE_URL + "/auth/profile");
    return response.data; 
}