'use client'
import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
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

export default function OrderDetailPage() {
    const params = useParams()
    const router = useRouter()
    const id     = params.id as string

    const [order, setOrder]     = useState<Order | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchOrder = async () => {
            try {
                const data = await orderService.getOrder(parseInt(id))
                setOrder(data)
            } catch (err: any) {
                if (err.response?.status === 401) router.push('/login')
            } finally {
                setLoading(false)
            }
        }
        fetchOrder()
    }, [id])

    if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">Loading...</div>
    if (!order)  return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">Order not found.</div>

    return (
        <div className="min-h-screen bg-gray-50">
           

            <div className="max-w-2xl mx-auto px-4 py-6 space-y-4">

                {/* Success banner for new orders */}
                {order.status === 'pending' && (
                    <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-center">
                        <p className="text-green-700 font-semibold">Order placed successfully!</p>
                        <p className="text-green-600 text-sm mt-1">The shop will confirm your order shortly.</p>
                    </div>
                )}

                {/* Order items */}
                <div className="bg-white rounded-xl border border-gray-200 p-5">
                    <h2 className="font-semibold text-gray-900 mb-3">Items</h2>
                    <div className="space-y-3">
                        {order.items.map((item) => (
                            <div key={item.id} className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-900">{item.product_name}</p>
                                    {item.cut_type_name && (
                                        <p className="text-xs text-gray-500">{item.cut_type_name}</p>
                                    )}
                                    <p className="text-xs text-gray-400">{item.quantity} kg × Rs.{item.unit_price}</p>
                                </div>
                                <p className="font-semibold text-gray-900 text-sm">Rs.{item.total_price}</p>
                            </div>
                        ))}
                    </div>
                    <div className="border-t pt-3 mt-3 space-y-1">
                        <div className="flex justify-between text-sm text-gray-600">
                            <span>Subtotal</span><span>Rs.{order.subtotal}</span>
                        </div>
                        <div className="flex justify-between text-sm text-gray-600">
                            <span>Delivery fee</span><span>Rs.{order.delivery_fee}</span>
                        </div>
                        <div className="flex justify-between font-bold text-gray-900">
                            <span>Total</span><span>Rs.{order.total_amount}</span>
                        </div>
                    </div>
                </div>

                {/* Delivery info */}
                <div className="bg-white rounded-xl border border-gray-200 p-5">
                    <h2 className="font-semibold text-gray-900 mb-3">Delivery info</h2>
                    <div className="space-y-1 text-sm text-gray-600">
                        <p><span className="font-medium text-gray-900">Name:</span> {order.delivery_name}</p>
                        <p><span className="font-medium text-gray-900">Phone:</span> {order.delivery_phone}</p>
                        <p><span className="font-medium text-gray-900">Address:</span> {order.delivery_address}</p>
                        <p><span className="font-medium text-gray-900">Payment:</span> {order.payment_method === 'cod' ? 'Cash on delivery' : 'Online'}</p>
                        {order.notes && <p><span className="font-medium text-gray-900">Notes:</span> {order.notes}</p>}
                    </div>
                </div>

                {/* Status history */}
                <div className="bg-white rounded-xl border border-gray-200 p-5">
                    <h2 className="font-semibold text-gray-900 mb-3">Order timeline</h2>
                    <div className="space-y-3">
                        {order.history.map((h, i) => (
                            <div key={i} className="flex items-start gap-3">
                                <div className="w-2 h-2 rounded-full bg-green-500 mt-1.5 shrink-0" />
                                <div>
                                    <p className="text-sm font-medium text-gray-900">
                                        {h.from_status ? `${STATUS_LABELS[h.from_status]} → ${STATUS_LABELS[h.to_status]}` : STATUS_LABELS[h.to_status]}
                                    </p>
                                    {h.note && <p className="text-xs text-gray-500">{h.note}</p>}
                                    <p className="text-xs text-gray-400">{new Date(h.created_at).toLocaleString()}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                
                  <a  href="/shops"
                    className="block w-full bg-white border border-gray-200 hover:border-green-500 text-gray-700 text-center font-medium py-3 rounded-xl transition-colors text-sm"
                >
                    Continue shopping
                </a>
            </div>
        </div>
    )
}