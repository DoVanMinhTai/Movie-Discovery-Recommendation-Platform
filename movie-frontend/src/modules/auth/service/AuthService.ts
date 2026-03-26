import apiClientService from "../../../common/services/ApiClientService";
import type { ProfileVm } from "../model/ProfileVm";

const baseUrl = process.env.REACT_APP_API_BASE_URL + "/auth";

export async function register(userName: string, email: string, password: string) {
    const response = await apiClientService.post(`${baseUrl}/register`, {
        userName,
        email,
        password
    });
    return response.data;
}

export async function login(email: string, password: string) : Promise<ProfileVm> {
    const response = await apiClientService.post(`${baseUrl}/login`, {
        email,
        password
    });
    return response.data;
}