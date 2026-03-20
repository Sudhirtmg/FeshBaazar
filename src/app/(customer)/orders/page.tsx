'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { orderService } from '@/services/orderService'
import { Order } from '@/types'

const STATUS_COLORS: { [key: string]: string } = {
    pending:          'bg-amber-50 text-amber-700',
    confirmed:        'bg-blue-50 text-blue-700',
    preparing:        'bg-purple-50 text-purple-700',
    out_for_delivery: 'bg-indigo-50 text-indigo-700',
    delivered:        'bg-green-50 text-green-700',
    cancelled:        'bg-red-50 text-red-700',
}

const STATUS_LABELS: { [key: string]: string } = {
    pending:          'Pending',
    confirmed:        'Confirmed',
    preparing:        'Preparing',
    out_for_delivery: 'Out for delivery',
    delivered:        'Delivered',
    cancelled:        'Cancelled',
}

export default function OrdersPage() {
    const router = useRouter()
    const [orders, setOrders]   = useState<Order[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchOrders = async () => {
            try {
                const data = await orderService.getOrders()
                setOrders(data)
            } catch (err: any) {
                if (err.response?.status === 401) router.push('/login')
            } finally {
                setLoading(false)
            }
        }
        fetchOrders()
    }, [])

    if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">Loading...</div>

    return (
        <div className="min-h-screen bg-gray-50">
            

            <div className="max-w-2xl mx-auto px-4 py-6">
                {orders.length === 0 ? (
                    <div className="text-center py-16">
                        <p className="text-gray-400 mb-4">No orders yet.</p>
                        <a href="/shops" className="bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-6 py-2.5 rounded-lg transition-colors">
                            Browse shops
                        </a>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {orders.map((order) => (
                            <a key={order.id} href={`/orders/${order.id}`} className="block bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md transition-shadow">
                                <div className="flex items-start justify-between mb-2">
                                    <div>
                                        <p className="font-semibold text-gray-900">Order #{order.id}</p>
                                        <p className="text-xs text-gray-500 mt-0.5">
                                            {new Date(order.created_at).toLocaleDateString('en-NP', {
                                                year: 'numeric', month: 'short', day: 'numeric',
                                                hour: '2-digit', minute: '2-digit'
                                            })}
                                        </p>
                                    </div>
                                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${STATUS_COLORS[order.status] || 'bg-gray-50 text-gray-600'}`}>
                                        {STATUS_LABELS[order.status] || order.status}
                                    </span>
                                </div>
                                <div className="text-xs text-gray-500 mb-2">
                                    {order.items.map(item => item.product_name).join(', ')}
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-xs text-gray-400">
                                        {order.delivery_address.startsWith('PICKUP') ? 'Pickup' : 'Delivery'}
                                    </span>
                                    <span className="font-semibold text-gray-900 text-sm">Rs.{order.total_amount}</span>
                                </div>
                            </a>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}