// src/services/orderService.ts
import api from '@/lib/api'
import { Order } from '@/types'

export const orderService = {
    checkout: async (data: {
        delivery_name: string
        delivery_phone: string
        delivery_address: string
        payment_method?: string
        notes?: string
    }): Promise<Order[]> => {
        const res = await api.post('/api/orders/checkout/', data)
        return res.data
    },

    getOrders: async (): Promise<Order[]> => {
        const res = await api.get('/api/orders/')
        return res.data
    },

    getOrder: async (id: number): Promise<Order> => {
        const res = await api.get(`/api/orders/${id}/`)
        return res.data
    },

    updateStatus: async (id: number, status: string, note?: string): Promise<Order> => {
        const res = await api.patch(`/api/orders/${id}/status/`, { status, note })
        return res.data
    },

    getShopOrders: async (): Promise<Order[]> => {
        const res = await api.get('/api/orders/shop-orders/')
        return res.data
    },
}