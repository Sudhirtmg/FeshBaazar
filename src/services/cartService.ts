// src/services/cartService.ts
import api from '@/lib/api'
import { Cart } from '@/types'

export const cartService = {
    getCart: async (): Promise<Cart> => {
        const res = await api.get('/api/cart/')
        return res.data
    },

    addItem: async (data: {
        product: number
        cut_type?: number
        quantity?: number
        amount?: number
    }): Promise<void> => {
        await api.post('/api/cart/items/', data)
    },

    updateItem: async (id: number, data: {
        quantity?: number
        amount?: number
    }): Promise<void> => {
        await api.patch(`/api/cart/items/${id}/`, data)
    },

    removeItem: async (id: number): Promise<void> => {
        await api.delete(`/api/cart/items/${id}/`)
    },

    clearCart: async (): Promise<void> => {
        await api.delete('/api/cart/')
    },
}