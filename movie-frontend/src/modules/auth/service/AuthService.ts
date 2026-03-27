import apiClientService from "../../../common/services/ApiClientService";
import type { ProfileVm } from "../model/ProfileVm";

const BASE_URL = import.meta.env.VITE_API_BASE_URL + "/auth";

export async function register(userName: string, email: string, password: string) {
    const response = await apiClientService.post(`${BASE_URL}/register`, {
        userName,
        email,
        password
    });
    return response.data;
}

export async function login(email: string, password: string) : Promise<ProfileVm> {
    const response = await apiClientService.post(`${BASE_URL}/login`, {
        email,
        password
    });
    return response.data;
}