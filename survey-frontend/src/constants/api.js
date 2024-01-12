import { authService } from '@/services/authService';
import { clearToken, getRefresh, getToken, setToken } from '@/utils/token';
import axios from 'axios'

export const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_HOST,
})


api.interceptors.response.use((res) => {
    return res.data
}, async (error) => {
    const originalRequest = error.config;
    // If the error status is 401 and there is no originalRequest._retry flag,
    // it means the token has expired and we need to refresh it
    if (error?.request?.status == 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        try {
            const refreshToken = getRefresh()
            const newToken = await authService.refreshToken({ refresh: refreshToken })
            setToken(newToken.access);
            // Retry the original request with the new token
            originalRequest.headers.Authorization = `Bearer ${newToken.access}`;
            return axios(originalRequest);
        } catch (error) {
            clearToken();
            window.location.href = '/login';
        }
    }
    return Promise.reject(error);
})

api.interceptors.request.use((config) => {
    const token = getToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
},
    (error) => Promise.reject(error))

export default api