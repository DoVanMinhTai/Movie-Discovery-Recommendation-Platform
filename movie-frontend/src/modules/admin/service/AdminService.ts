import apiClientService from "../../../common/services/ApiClientService";

export const adminService = {
    getStats: (from?: string, to?: string) => {
        const params: Record<string, string> = {};
        if (from) params.from = from;
        if (to) params.to = to;
        return apiClientService.get('/admin/statistics', { params });
    },
    getMovies: () => apiClientService.get('/admin/movie/movies'),
    deleteMovie: (id: number, adminPass: string) => apiClientService.delete(`/admin/movie/movies/${id}`, {
        headers: { 'X-Admin-Password': adminPass }
    }),
    addMovie: (movie: any, adminPass: string) => apiClientService.post('/admin/movie/movies', movie, {
        headers: { 'X-Admin-Password': adminPass }
    }),
    updateMovie: (movie: any, adminPass: string) => apiClientService.put('/admin/movie/movies', movie, {
        headers: { 'X-Admin-Password': adminPass }
    }),
    getUsers: () => apiClientService.get('/admin/user/users'),
    deleteUser: (id: number) => apiClientService.delete(`/admin/user/${id}`),
    checkDuplicate: (title: string, year: number, excludeId?: number) => {
        const params: Record<string, string | number> = { title, year };
        if (excludeId) params.excludeId = excludeId;
        return apiClientService.get('/admin/movie/check-duplicate', { params });
    },
    getGenres: () => apiClientService.get('/category/genres'),
};