const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function sendMessage(currentInput: any) {
    const response = await fetch(BASE_URL + "/chatbot/message", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({ message: currentInput }),
    });
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Lỗi server: ${response.status}`);
    }
    
    return response;
}