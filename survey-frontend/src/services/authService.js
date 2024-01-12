import api from "@/constants/api";
import { setToken } from "@/utils/token";
import { jwtDecode } from "jwt-decode";

export const authService = {
    async login(data) {
        const response = await api.post('/api/v1/token', data)
        if (response.access) {
            const { access, refresh } = response

            const claim = jwtDecode(access);
            setToken(access)
            localStorage.setItem('claim', JSON.stringify(claim))
            localStorage.setItem('refresh', JSON.stringify(refresh))

            return true
        }
        return false;
    },

    refreshToken(data) {
        return api.post('/api/v1/token/refresh', data)
    },

    verifyToken(data) {
        return api.post('/api/v1/token/verify', data)
    }
}