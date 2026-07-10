import axios, { type AxiosRequestConfig, type AxiosInstance, type AxiosResponse } from "axios";
import { HandleError, handleHttpStatus } from "./error/HandleError";
import type { ApiResponse } from "./ApiResponse";
import { toast } from "react-hot-toast";
import { config } from "process";

export interface PageAbleResponse {
    content: any[];
    totalPages: number;
    totalElements: number;
    size: number;
    number: number;
}

const axiosInstance: AxiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || "",
    headers: {
        'Content-Type': 'application/json; charset=UTF-8'
    },
    timeout: 10000
});

axiosInstance.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }

    const hfToken = import.meta.env.VITE_HF_TOKEN;
    if (hfToken) {
        config.headers['X-HF-Token'] = hfToken;
    }

    return config;
}, (error) => {
    if (error.response) {
        throw new HandleError(error.response.data);
    }
    throw error;
});

axiosInstance.interceptors.response.use(
    (response: AxiosResponse<ApiResponse<any>>) => {
        const apiData = response.data;
        if (apiData.code && apiData.code !== 1000) {
            toast.error(apiData.message || "Đã có lỗi xảy ra");
            return Promise.reject(new HandleError(apiData.message, apiData.code, response.status));
        }
        return response.data.result; 
    },
    (error) => {
        let errorMessage = "Lỗi kết nối đến server";
        let code = 9999;
        let status = 500;

        if (error.response) {
            const data = error.response.data as ApiResponse<any>;
            console.error("API Error Response:", data);
            errorMessage = data.message || errorMessage;
            code = data.code || code;
            status = error.response.status;

            errorMessage = handleHttpStatus(status, errorMessage);

            if (status === 401 || code === 1004) {
                localStorage.removeItem("token");
                window.location.href = "/login";
            } else if (status === 403 || code === 1005) {
                window.location.href = "/forbidden";
            } 

        } else if (error.request) {
            errorMessage = "Không nhận được phản hồi từ server";
        } else if (error.message) {
            errorMessage = error.message;
        }

        toast.error(errorMessage);
        return Promise.reject(new HandleError(errorMessage, code, status));
    }
);


const apiClientService = {
    get: <T = any>(endpoint: string, config?: AxiosRequestConfig): Promise<T> => axiosInstance.get(endpoint, config),
    post: <T = any>(endpoint: string, data?: any, config?: AxiosRequestConfig): Promise<T> => axiosInstance.post(endpoint, data, config),
    put: <T = any>(endpoint: string, data?: any, config?: AxiosRequestConfig): Promise<T> => axiosInstance.put(endpoint, data, config),
    delete: <T = any>(endpoint: string, config?: AxiosRequestConfig): Promise<T> => axiosInstance.delete(endpoint, config),
}

export default apiClientService;