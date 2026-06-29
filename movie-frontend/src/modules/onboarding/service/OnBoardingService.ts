import apiClientService from "../../../common/services/ApiClientService";
import { API_ENDPOINTS } from "../../../constants/ApiEndpoints";

export class MissingAuthTokenError extends Error {
    readonly code = "AUTH_MISSING_TOKEN";
    constructor() {
        super("Missing authentication token");
        this.name = "MissingAuthTokenError";
    }
}

export async function submitOnBoarding({ genres }: { genres: number[] }) {
    const token = localStorage.getItem("token");
    if (!token) {
        throw new MissingAuthTokenError();
    }
    return apiClientService.post<{ token: string }>(API_ENDPOINTS.ONBOARDING.POST, { genres });
}