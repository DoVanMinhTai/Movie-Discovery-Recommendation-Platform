import { API_ENDPOINTS } from "../../../common/constants/ApiEndpoints";
import apiClientService from "../../../common/services/ApiClientService";
import type { ProfileGetVm } from "../model/ProfileGetVm";
import type { RegisterGetVm } from "../model/RegisterGetVm";

export async function register(userName: string, email: string, password: string) : Promise<RegisterGetVm> {
    const response = await apiClientService.post(API_ENDPOINTS.AUTH.REGISTER, {
        userName,
        email,
        password
    });
    return response.data;
}

export async function login(email: string, password: string) : Promise<ProfileGetVm> {
    const response = await apiClientService.post(API_ENDPOINTS.AUTH.LOGIN, {
        email,
        password
    });
    return response.data;
}

export async function getMyProfile() : Promise<ProfileGetVm> {
    const response = await apiClientService.get(API_ENDPOINTS.AUTH.GET_PROFILE);
    return response.data; 
}

export async function existEmail(email: string) {
    const response = await apiClientService.get(API_ENDPOINTS.AUTH.EXIST_EMAIL, {
        params: { email }
    });
    return response.data;
}
