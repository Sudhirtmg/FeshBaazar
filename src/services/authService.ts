// src/services/authService.ts
import api from '@/lib/api'
import { User } from '@/types'

interface LoginResponse {
    user: User
    tokens: {
        access: string
        refresh: string
    }
}

interface RegisterData {
    phone: string
    email: string
    password: string
    role: string
}

export const authService = {
    login: async (phone: string, password: string): Promise<LoginResponse> => {
        const res = await api.post('/api/auth/login/', { phone, password })
        return res.data
    },
    register: async (data: RegisterData): Promise<LoginResponse> => {
        const res = await api.post('/api/auth/register/', data)
        return res.data
    },
    me: async (): Promise<User> => {
        const res = await api.get('/api/auth/me/')
        return res.data
    },
}