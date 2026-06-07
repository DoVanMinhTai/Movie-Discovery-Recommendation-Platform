export class HandleError extends Error {
    code?: number;
    status?: number;

    constructor(message: string, code?: number, status?: number) {
        super(message);
        this.code = code;
        this.status = status;
        Object.setPrototypeOf(this, HandleError.prototype);
    }
}

export const handleHttpStatus = (status: number, backendMessage?: string): string => {

    if (backendMessage) return backendMessage;

    switch (status) {
        case 400: return "Yêu cầu không hợp lệ (Bad Request)";
        case 401: return "Phiên đăng nhập đã hết hạn (Unauthorized)";
        case 403: return "Bạn không có quyền truy cập (Forbidden)";
        case 404: return "Không tìm thấy tài nguyên (Not Found)";
        case 429: return "Bạn đã thao tác quá nhanh, vui lòng thử lại sau (Too Many Requests)";
        case 500: return "Lỗi hệ thống phía server (Internal Server Error)";
        case 503: return "Dịch vụ đang được bảo trì (Service Unavailable)";
        default: return `Đã xảy ra lỗi không xác định (Status: ${status})`;
    }
}