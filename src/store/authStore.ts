import { create } from 'zustand'
import Cookies from 'js-cookie'
import { User } from '@/types'

interface AuthState {
    user: User | null
    isAuthenticated: boolean
    setUser: (user: User) => void
    logout: () => void
}

const useAuthStore = create<AuthState>((set) => ({
    user: null,
    isAuthenticated: false,

    setUser: (user) => set({ user, isAuthenticated: true }),

    logout: () => {
        Cookies.remove('access_token')
        Cookies.remove('refresh_token')
        set({ user: null, isAuthenticated: false })
    },
}))

export default useAuthStore
