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
    const response = await fetch(API_ENDPOINTS.ONBOARDING.POST, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ genres })
    });

    console.log("OnBoarding response:", response);
    if (!response.ok) {
        throw new Error("Failed to submit onboarding");
    }
    return response.text();
}