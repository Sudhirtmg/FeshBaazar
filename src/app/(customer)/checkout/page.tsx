'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { orderService } from '@/services/orderService'
import { cartService } from '@/services/cartService'
import { shopService } from '@/services/shopService'
import { Shop } from '@/types'

export default function CheckoutPage() {
    const router = useRouter()
    const [shop, setShop]           = useState<Shop | null>(null)
    const [fulfillment, setFulfillment] = useState<'delivery' | 'pickup'>('delivery')
    const [form, setForm] = useState({
        delivery_name:    '',
        delivery_phone:   '',
        delivery_address: '',
        payment_method:   'cod',
        notes:            '',
    })
    const [loading, setLoading] = useState(false)
    const [pageLoading, setPageLoading] = useState(true)
    const [error, setError] = useState('')

   useEffect(() => {
    const loadShop = async () => {
        try {
            const cart = await cartService.getCart()
            if (cart.items.length === 0) {
                router.push('/cart')
                return
            }
            const shops = await shopService.getShops()
            const shop  = shops.find(s => s.name === cart.items[0].shop_name)
            if (shop) {
                setShop(shop)
                // if shop has no delivery, force pickup
                if (!shop.has_delivery) {
                    setFulfillment('pickup')
                }
                // if shop has no pickup, force delivery
                if (!shop.has_pickup) {
                    setFulfillment('delivery')
                }
            }
        } catch (err) {
            console.error(err)
        } finally {
            setPageLoading(false)
        }
    }
    loadShop()
}, [])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        try {
            const payload = {
                ...form,
                delivery_address: fulfillment === 'pickup'
                    ? `PICKUP — ${shop?.address}`
                    : form.delivery_address,
                delivery_name: form.delivery_name || 'Pickup',
                delivery_phone: form.delivery_phone || shop?.phone || '',
                notes: fulfillment === 'pickup'
                    ? `Pickup order. ${form.notes}`
                    : form.notes,
            }
            const orders = await orderService.checkout(payload)
            router.push(`/orders/${orders[0].id}`)
        } catch (err: any) {
            if (err.response?.status === 401) router.push('/login')
            else setError(err.response?.data?.detail || 'Checkout failed.')
        } finally {
            setLoading(false)
        }
    }

    if (pageLoading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">Loading...</div>

    return (
        <div className="min-h-screen bg-gray-50">
            

            <div className="max-w-2xl mx-auto px-4 py-6">
                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">

                    {/* Fulfillment method */}
                    {shop && (shop.has_delivery && shop.has_pickup) && (
                        <div className="bg-white rounded-xl border border-gray-200 p-5">
                            <h2 className="font-semibold text-gray-900 mb-3">How do you want to receive your order?</h2>
                            <div className="flex gap-3">
                                <button
                                    type="button"
                                    onClick={() => setFulfillment('delivery')}
                                    className={`flex-1 py-3 rounded-xl border-2 text-sm font-medium transition-colors ${
                                        fulfillment === 'delivery'
                                            ? 'border-green-600 bg-green-50 text-green-700'
                                            : 'border-gray-200 text-gray-600'
                                    }`}
                                >
                                    Delivery
                                    <p className="text-xs font-normal mt-0.5 opacity-70">Delivered to your address</p>
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setFulfillment('pickup')}
                                    className={`flex-1 py-3 rounded-xl border-2 text-sm font-medium transition-colors ${
                                        fulfillment === 'pickup'
                                            ? 'border-green-600 bg-green-50 text-green-700'
                                            : 'border-gray-200 text-gray-600'
                                    }`}
                                >
                                    Pickup
                                    <p className="text-xs font-normal mt-0.5 opacity-70">Collect from shop</p>
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Pickup only notice */}
                    {shop && !shop.has_delivery && shop.has_pickup && (
                        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                            <p className="text-sm font-medium text-amber-800">This shop does not offer delivery</p>
                            <p className="text-xs text-amber-600 mt-1">You can pick up your order from: {shop.address}</p>
                        </div>
                    )}

                    {/* Delivery details — only show if delivery selected */}
                    {fulfillment === 'delivery' && (
                        <div className="bg-white rounded-xl border border-gray-200 p-5">
                            <h2 className="font-semibold text-gray-900 mb-4">Delivery details</h2>
                            <div className="space-y-3">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Full name</label>
                                    <input
                                        type="text"
                                        value={form.delivery_name}
                                        onChange={(e) => setForm({ ...form, delivery_name: e.target.value })}
                                        placeholder="Ram Shrestha"
                                        className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                                    <input
                                        type="text"
                                        value={form.delivery_phone}
                                        onChange={(e) => setForm({ ...form, delivery_phone: e.target.value })}
                                        placeholder="+9779800000001"
                                        className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Delivery address</label>
                                    <textarea
                                        value={form.delivery_address}
                                        onChange={(e) => setForm({ ...form, delivery_address: e.target.value })}
                                        placeholder="Kathmandu-10, Baneshwor"
                                        rows={2}
                                        className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                        required
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Pickup details */}
                    {fulfillment === 'pickup' && (
                        <div className="bg-white rounded-xl border border-gray-200 p-5">
                            <h2 className="font-semibold text-gray-900 mb-3">Pickup details</h2>
                            <div className="bg-gray-50 rounded-lg p-3 mb-3">
                                <p className="text-xs text-gray-500 mb-1">Pickup from</p>
                                <p className="text-sm font-medium text-gray-900">{shop?.name}</p>
                                <p className="text-xs text-gray-500">{shop?.address}</p>
                                <p className="text-xs text-gray-500">{shop?.phone}</p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Your phone (for confirmation)</label>
                                <input
                                    type="text"
                                    value={form.delivery_phone}
                                    onChange={(e) => setForm({ ...form, delivery_phone: e.target.value })}
                                    placeholder="+9779800000001"
                                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                    required
                                />
                            </div>
                        </div>
                    )}

                    {/* Notes */}
                    <div className="bg-white rounded-xl border border-gray-200 p-5">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
                        <input
                            type="text"
                            value={form.notes}
                            onChange={(e) => setForm({ ...form, notes: e.target.value })}
                            placeholder="Any special instructions..."
                            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                    </div>

                    {/* Payment */}
                    <div className="bg-white rounded-xl border border-gray-200 p-5">
                        <h2 className="font-semibold text-gray-900 mb-4">Payment method</h2>
                        <div className="space-y-2">
                            <label className="flex items-center gap-3 cursor-pointer">
                                <input
                                    type="radio"
                                    name="payment"
                                    value="cod"
                                    checked={form.payment_method === 'cod'}
                                    onChange={() => setForm({ ...form, payment_method: 'cod' })}
                                    className="text-green-600"
                                />
                                <div>
                                    <p className="text-sm font-medium text-gray-900">Cash on delivery</p>
                                    <p className="text-xs text-gray-500">Pay when your order arrives</p>
                                </div>
                            </label>
                            <label className="flex items-center gap-3 cursor-pointer opacity-50">
                                <input type="radio" name="payment" value="online" disabled />
                                <div>
                                    <p className="text-sm font-medium text-gray-900">Online payment</p>
                                    <p className="text-xs text-gray-500">Coming soon</p>
                                </div>
                            </label>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 rounded-xl transition-colors disabled:opacity-50"
                    >
                        {loading ? 'Placing order...' : 'Place order'}
                    </button>
                </form>
            </div>
        </div>
    )
}