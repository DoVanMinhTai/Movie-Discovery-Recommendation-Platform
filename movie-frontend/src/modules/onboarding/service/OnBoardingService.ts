import { API_ENDPOINTS } from "../../../constants/ApiEndpoints";

export async function submitOnBoarding({ genres }: { genres: number[] }) {
    const token = localStorage.getItem("token");
    const response = await fetch(API_ENDPOINTS.ONBOARDING.POST, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ genres })
    });
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Lỗi server: ${response.status}`);
    }
    return response.json();
}