// src/services/shopService.ts
import api from '@/lib/api'
import { Shop, ShopSchedule } from '@/types'

export const shopService = {
    getShops: async (city?: string): Promise<Shop[]> => {
        const params = city ? { city } : {}
        const res = await api.get('/api/shops/', { params })
        return res.data
    },

    getShop: async (slug: string): Promise<Shop> => {
        const res = await api.get(`/api/shops/${slug}/`)
        return res.data
    },

    getMyShop: async (): Promise<Shop> => {
        const res = await api.get('/api/shops/my-shop/')
        return res.data
    },

    updateMyShop: async (data: FormData): Promise<Shop> => {
        const res = await api.patch('/api/shops/onboarding/', data)
        return res.data
    },

    becomeShopOwner: async (): Promise<{ detail: string; shop: Shop }> => {
        const res = await api.post('/api/shops/become-shop-owner/')
        return res.data
    },

    // ✅ Schedule endpoints
    getSchedule: async (): Promise<ShopSchedule[]> => {
        const res = await api.get('/api/shops/schedule/')
        return res.data
    },

   updateSchedule: async (schedules: Omit<ShopSchedule, 'id' | 'weekday_name'>[]): Promise<ShopSchedule[]> => {
        const res = await api.post('/api/shops/schedule/', { schedules })
        return res.data
    },
}