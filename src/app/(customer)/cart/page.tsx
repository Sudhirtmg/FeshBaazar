'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { cartService } from '@/services/cartService'
import { Cart } from '@/types'

export default function CartPage() {
    const router = useRouter()
    const [cart, setCart] = useState<Cart | null>(null)
    const [loading, setLoading] = useState(true)
    const [removing, setRemoving] = useState<{ [id: number]: boolean }>({})

    const fetchCart = async () => {
        try {
            const data = await cartService.getCart()
            setCart(data)
        } catch (err: any) {
            if (err.response?.status === 401) router.push('/login')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { fetchCart() }, [])

    const handleRemove = async (itemId: number) => {
        setRemoving(prev => ({ ...prev, [itemId]: true }))
        try {
            await cartService.removeItem(itemId)
            await fetchCart()
        } finally {
            setRemoving(prev => ({ ...prev, [itemId]: false }))
        }
    }

    if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">Loading...</div>

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="bg-white border-b border-gray-200 px-4 py-4">
                <div className="max-w-2xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <a href="/shops" className="text-gray-400 hover:text-gray-600 text-sm">← Shops</a>
                        <span className="font-bold text-gray-900">Your Cart</span>
                    </div>
                    {cart && cart.item_count > 0 && (
                        <button onClick={() => cartService.clearCart().then(fetchCart)} className="text-sm text-red-500 hover:text-red-700">
                            Clear all
                        </button>
                    )}
                </div>
            </div>

            <div className="max-w-2xl mx-auto px-4 py-6">
                {!cart || cart.item_count === 0 ? (
                    <div className="text-center py-16">
                        <p className="text-gray-400 mb-4">Your cart is empty.</p>
                        <a href="/shops" className="bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-6 py-2.5 rounded-lg transition-colors">
                            Browse shops
                        </a>
                    </div>
                ) : (
                    <>
                        <div className="space-y-3 mb-6">
                            {cart.items.map((item) => (
                                <div key={item.id} className="bg-white rounded-xl border border-gray-200 p-4">
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <p className="font-medium text-gray-900">{item.product_name}</p>
                                            {item.cut_type_name && <p className="text-xs text-gray-500 mt-0.5">{item.cut_type_name}</p>}
                                            <p className="text-xs text-gray-400 mt-0.5">{item.shop_name}</p>
                                        </div>
                                        <button
                                            onClick={() => handleRemove(item.id)}
                                            disabled={removing[item.id]}
                                            className="text-red-400 hover:text-red-600 text-sm ml-4"
                                        >
                                            {removing[item.id] ? '...' : 'Remove'}
                                        </button>
                                    </div>
                                    <div className="flex items-center justify-between mt-3">
                                        <p className="text-xs text-gray-500">{item.quantity} kg × Rs.{item.price_at_time}</p>
                                        <p className="font-semibold text-green-700 text-sm">Rs.{item.subtotal}</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
                            <div className="flex justify-between text-sm text-gray-600 mb-2">
                                <span>Subtotal</span><span>Rs.{cart.total}</span>
                            </div>
                            <div className="flex justify-between text-sm text-gray-600 mb-3">
                                <span>Delivery fee</span><span>Rs.50.00</span>
                            </div>
                            <div className="flex justify-between font-bold text-gray-900 border-t pt-3">
                                <span>Total</span>
                                <span>Rs.{(parseFloat(cart.total) + 50).toFixed(2)}</span>
                            </div>
                        </div>

                        <a href="/checkout" className="block w-full bg-green-600 hover:bg-green-700 text-white text-center font-medium py-3 rounded-xl transition-colors">
                            Proceed to checkout
                        </a>
                    </>
                )}
            </div>
        </div>
    )
}