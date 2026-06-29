export interface ApiResponse<T> {
    message: string;
    code?: number; 
    result: T;
}
