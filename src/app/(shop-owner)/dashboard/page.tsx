// 'use client'
// import { useEffect, useRef, useState, useCallback } from 'react'
// import { useRouter } from 'next/navigation'
// import { orderService } from '@/services/orderService'
// import { Order } from '@/types'

// const STATUS_COLORS: { [key: string]: string } = {
//     pending:          'bg-amber-50 text-amber-700',
//     confirmed:        'bg-blue-50 text-blue-700',
//     preparing:        'bg-purple-50 text-purple-700',
//     out_for_delivery: 'bg-indigo-50 text-indigo-700',
//     delivered:        'bg-green-50 text-green-700',
//     cancelled:        'bg-red-50 text-red-700',
// }

// const STATUS_LABELS: { [key: string]: string } = {
//     pending:          'Pending',
//     confirmed:        'Confirmed',
//     preparing:        'Preparing',
//     out_for_delivery: 'Out for delivery',
//     delivered:        'Delivered',
//     cancelled:        'Cancelled',
// }

// const NEXT_STATUS: { [key: string]: { value: string, label: string } } = {
//     pending:          { value: 'confirmed',        label: 'Confirm order' },
//     confirmed:        { value: 'preparing',        label: 'Start preparing' },
//     preparing:        { value: 'out_for_delivery', label: 'Send for delivery' },
//     out_for_delivery: { value: 'delivered',        label: 'Mark delivered' },
// }

// export default function DashboardPage() {
//     const router = useRouter()
//     const [orders, setOrders]     = useState<Order[]>([])
//     const [loading, setLoading]   = useState(true)
//     const [updating, setUpdating] = useState<{ [id: number]: boolean }>({})
//     const [filter, setFilter]     = useState('pending')
//     const [lastRefresh, setLastRefresh] = useState<Date>(new Date())
//     const prevOrderCount = useRef<number>(0)

//     const playSound = () => {
//         try {
//             const ctx  = new AudioContext()
//             const osc  = ctx.createOscillator()
//             const gain = ctx.createGain()
//             osc.connect(gain)
//             gain.connect(ctx.destination)
//             osc.frequency.setValueAtTime(880, ctx.currentTime)
//             osc.frequency.setValueAtTime(660, ctx.currentTime + 0.1)
//             osc.frequency.setValueAtTime(880, ctx.currentTime + 0.2)
//             gain.gain.setValueAtTime(0.3, ctx.currentTime)
//             gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5)
//             osc.start(ctx.currentTime)
//             osc.stop(ctx.currentTime + 0.5)
//         } catch (err) {
//             console.log('Audio not available')
//         }
//     }

//     const showBrowserNotification = (count: number) => {
//         if ('Notification' in window && Notification.permission === 'granted') {
//             new Notification('FreshBazaar — New Order!', {
//                 body: `You have ${count} new order${count > 1 ? 's' : ''} waiting.`,
//                 icon: '/favicon.ico',
//             })
//         }
//     }

//     // replace the fetchOrders function
// const fetchOrders = useCallback(async (isPolling = false) => {
//     try {
//         const data = await orderService.getShopOrders()
//         setOrders(data)
//         setLastRefresh(new Date())

//         const pendingCount = data.filter(o => o.status === 'pending').length

//         if (isPolling) {
//             const lastKnown = parseInt(localStorage.getItem('fb_pending_count') || '0')
//             if (pendingCount > lastKnown) {
//                 playSound()
//                 showBrowserNotification(pendingCount - lastKnown)
//             }
//         }

//         localStorage.setItem('fb_pending_count', pendingCount.toString())
//         prevOrderCount.current = pendingCount

//     } catch (err: any) {
//         if (err.response?.status === 401) router.push('/login')
//         if (err.response?.status === 403) router.push('/shops')
//     } finally {
//         setLoading(false)
//     }
// }, [router])

//     useEffect(() => {
//         if ('Notification' in window && Notification.permission === 'default') {
//             Notification.requestPermission()
//         }
//         fetchOrders(false)
//         const interval = setInterval(() => fetchOrders(true), 30000)
//         return () => clearInterval(interval)
//     }, [fetchOrders])

//     const handleStatusUpdate = async (order: Order, newStatus: string) => {
//         setUpdating(prev => ({ ...prev, [order.id]: true }))
//         try {
//             await orderService.updateStatus(order.id, newStatus)
//             await fetchOrders(false)
//         } finally {
//             setUpdating(prev => ({ ...prev, [order.id]: false }))
//         }
//     }

//     const handleCancel = async (order: Order) => {
//         if (!confirm('Cancel this order?')) return
//         setUpdating(prev => ({ ...prev, [order.id]: true }))
//         try {
//             await orderService.updateStatus(order.id, 'cancelled', 'Cancelled by shop')
//             await fetchOrders(false)
//         } finally {
//             setUpdating(prev => ({ ...prev, [order.id]: false }))
//         }
//     }

//     const filteredOrders = filter === 'all'
//         ? orders
//         : orders.filter(o => o.status === filter)

//     const counts: { [key: string]: number } = {}
//     orders.forEach(o => { counts[o.status] = (counts[o.status] || 0) + 1 })

//     if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">Loading...</div>

//     return (
//         <div className="min-h-screen bg-gray-50">
//             <div className="max-w-4xl mx-auto px-4 py-6">

//                 {/* Header */}
//                 <div className="flex items-center justify-between mb-6">
//                     <div className="flex items-center gap-3">
//                         <h1 className="text-xl font-bold text-gray-900">Incoming Orders</h1>
//                         <span className="text-xs text-gray-400">
//                             Updated {lastRefresh.toLocaleTimeString()}
//                         </span>
//                     </div>
//                     <div className="flex gap-2">
//     <button
//         onClick={() => { playSound(); showBrowserNotification(1) }}
//         className="text-xs text-gray-500 hover:text-gray-700 border border-gray-200 px-3 py-1.5 rounded-lg transition-colors"
//     >
//         Test sound
//     </button>
//     <button
//         onClick={() => fetchOrders(false)}
//         className="text-xs text-green-600 hover:text-green-700 border border-green-200 px-3 py-1.5 rounded-lg transition-colors"
//     >
//         Refresh
//     </button>
// </div>
//                 </div>

//                 {/* Stats */}
//                 <div className="grid grid-cols-3 gap-3 mb-6">
//                     <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
//                         <p className="text-2xl font-bold text-amber-600">{counts['pending'] || 0}</p>
//                         <p className="text-xs text-gray-500 mt-1">Pending</p>
//                     </div>
//                     <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
//                         <p className="text-2xl font-bold text-blue-600">{(counts['confirmed'] || 0) + (counts['preparing'] || 0)}</p>
//                         <p className="text-xs text-gray-500 mt-1">In progress</p>
//                     </div>
//                     <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
//                         <p className="text-2xl font-bold text-green-600">{counts['delivered'] || 0}</p>
//                         <p className="text-xs text-gray-500 mt-1">Delivered</p>
//                     </div>
//                 </div>

//                 {/* Filter tabs */}
//                 <div className="flex gap-2 mb-4 overflow-x-auto">
//                     {['pending', 'confirmed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled', 'all'].map((s) => (
//                         <button
//                             key={s}
//                             onClick={() => setFilter(s)}
//                             className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
//                                 filter === s
//                                     ? 'bg-green-600 text-white'
//                                     : 'bg-white border border-gray-200 text-gray-600'
//                             }`}
//                         >
//                             {STATUS_LABELS[s] || 'All'}
//                             {counts[s] ? ` (${counts[s]})` : ''}
//                         </button>
//                     ))}
//                 </div>

//                 {/* Orders */}
//                 {filteredOrders.length === 0 ? (
//                     <div className="text-center py-12 text-gray-400">No orders here.</div>
//                 ) : (
//                     <div className="space-y-4">
//                         {filteredOrders.map((order) => (
//                             <div key={order.id} className="bg-white rounded-xl border border-gray-200 p-5">
//                                 <div className="flex items-start justify-between mb-3">
//                                     <div>
//                                         <p className="font-semibold text-gray-900">Order #{order.id}</p>
//                                         <p className="text-xs text-gray-500 mt-0.5">
//                                             {new Date(order.created_at).toLocaleString()}
//                                         </p>
//                                     </div>
//                                     <span className={`text-xs font-medium px-2 py-1 rounded-full ${STATUS_COLORS[order.status]}`}>
//                                         {STATUS_LABELS[order.status]}
//                                     </span>
//                                 </div>

//                                 <div className="bg-gray-50 rounded-lg p-3 mb-3">
//                                     {order.items.map((item) => (
//                                         <div key={item.id} className="flex justify-between text-sm py-0.5">
//                                             <span className="text-gray-700">
//                                                 {item.product_name}
//                                                 {item.cut_type_name && ` (${item.cut_type_name})`}
//                                                 {' — '}{item.quantity} kg
//                                             </span>
//                                             <span className="text-gray-900 font-medium">Rs.{item.total_price}</span>
//                                         </div>
//                                     ))}
//                                     <div className="border-t mt-2 pt-2 flex justify-between text-sm font-semibold">
//                                         <span>Total</span>
//                                         <span>Rs.{order.total_amount}</span>
//                                     </div>
//                                 </div>

//                                 <div className="text-xs text-gray-500 mb-3 space-y-0.5">
//                                     <p>{order.delivery_address.startsWith('PICKUP') ? 'PICKUP' : `Deliver to: ${order.delivery_address}`}</p>
//                                     <p>Contact: {order.delivery_name} — {order.delivery_phone}</p>
//                                     {order.notes && <p>Note: {order.notes}</p>}
//                                 </div>

//                                 <div className="flex gap-2">
//                                     {NEXT_STATUS[order.status] && (
//                                         <button
//                                             onClick={() => handleStatusUpdate(order, NEXT_STATUS[order.status].value)}
//                                             disabled={updating[order.id]}
//                                             className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-2 rounded-lg transition-colors disabled:opacity-50"
//                                         >
//                                             {updating[order.id] ? '...' : NEXT_STATUS[order.status].label}
//                                         </button>
//                                     )}
//                                     {['pending', 'confirmed'].includes(order.status) && (
//                                         <button
//                                             onClick={() => handleCancel(order)}
//                                             disabled={updating[order.id]}
//                                             className="px-4 bg-red-50 hover:bg-red-100 text-red-600 text-sm font-medium py-2 rounded-lg transition-colors disabled:opacity-50"
//                                         >
//                                             Cancel
//                                         </button>
//                                     )}
//                                 </div>
//                             </div>
//                         ))}
//                     </div>
//                 )}
//             </div>
//         </div>
//     )
// }



'use client'
import { useEffect, useRef, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { orderService } from '@/services/orderService'
import { shopService } from '@/services/shopService'
import { Order, Shop } from '@/types'

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

const NEXT_STATUS: { [key: string]: { value: string, label: string } } = {
    pending:          { value: 'confirmed',        label: 'Confirm order' },
    confirmed:        { value: 'preparing',        label: 'Start preparing' },
    preparing:        { value: 'out_for_delivery', label: 'Send for delivery' },
    out_for_delivery: { value: 'delivered',        label: 'Mark delivered' },
}

export default function DashboardPage() {
    const router = useRouter()
    const [orders, setOrders]     = useState<Order[]>([])
    const [shop, setShop]         = useState<Shop | null>(null)
    const [loading, setLoading]   = useState(true)
    const [updating, setUpdating] = useState<{ [id: number]: boolean }>({})
    const [filter, setFilter]     = useState('pending')
    const [lastRefresh, setLastRefresh] = useState<Date>(new Date())
    const prevOrderCount = useRef<number>(0)

    const playSound = () => {
        try {
            const ctx  = new AudioContext()
            const osc  = ctx.createOscillator()
            const gain = ctx.createGain()
            osc.connect(gain)
            gain.connect(ctx.destination)
            osc.frequency.setValueAtTime(880, ctx.currentTime)
            osc.frequency.setValueAtTime(660, ctx.currentTime + 0.1)
            osc.frequency.setValueAtTime(880, ctx.currentTime + 0.2)
            gain.gain.setValueAtTime(0.3, ctx.currentTime)
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5)
            osc.start(ctx.currentTime)
            osc.stop(ctx.currentTime + 0.5)
        } catch (err) {
            console.log('Audio not available')
        }
    }

    const showBrowserNotification = (count: number) => {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('FreshBazaar — New Order!', {
                body: `You have ${count} new order${count > 1 ? 's' : ''} waiting.`,
                icon: '/favicon.ico',
            })
        }
    }

    const fetchOrders = useCallback(async (isPolling = false) => {
        try {
            const data = await orderService.getShopOrders()
            setOrders(data)
            setLastRefresh(new Date())

            const pendingCount = data.filter(o => o.status === 'pending').length

            if (isPolling) {
                const lastKnown = parseInt(localStorage.getItem('fb_pending_count') || '0')
                if (pendingCount > lastKnown) {
                    playSound()
                    showBrowserNotification(pendingCount - lastKnown)
                }
            }

            localStorage.setItem('fb_pending_count', pendingCount.toString())
            prevOrderCount.current = pendingCount

        } catch (err: any) {
            if (err.response?.status === 401) router.push('/login')
            if (err.response?.status === 403) router.push('/shops')
        } finally {
            setLoading(false)
        }
    }, [router])

    useEffect(() => {
        // ✅ Load shop status alongside orders
        const init = async () => {
            try {
                const [shopData] = await Promise.allSettled([
                    shopService.getMyShop(),
                ])
                if (shopData.status === 'fulfilled') setShop(shopData.value)
            } catch {}
        }

        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission()
        }
        init()
        fetchOrders(false)
        const interval = setInterval(() => fetchOrders(true), 30000)
        return () => clearInterval(interval)
    }, [fetchOrders])

    const handleStatusUpdate = async (order: Order, newStatus: string) => {
        setUpdating(prev => ({ ...prev, [order.id]: true }))
        try {
            await orderService.updateStatus(order.id, newStatus)
            await fetchOrders(false)
        } finally {
            setUpdating(prev => ({ ...prev, [order.id]: false }))
        }
    }

    const handleCancel = async (order: Order) => {
        if (!confirm('Cancel this order?')) return
        setUpdating(prev => ({ ...prev, [order.id]: true }))
        try {
            await orderService.updateStatus(order.id, 'cancelled', 'Cancelled by shop')
            await fetchOrders(false)
        } finally {
            setUpdating(prev => ({ ...prev, [order.id]: false }))
        }
    }

    const filteredOrders = filter === 'all'
        ? orders
        : orders.filter(o => o.status === filter)

    const counts: { [key: string]: number } = {}
    orders.forEach(o => { counts[o.status] = (counts[o.status] || 0) + 1 })

    if (loading) return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">
            Loading...
        </div>
    )

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-4xl mx-auto px-4 py-6">

                {/* ✅ Pending verification banner */}
                {shop && !shop.is_verified && (
                    <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start justify-between gap-4">
                        <div>
                            <p className="text-sm font-medium text-amber-800">
                                Your shop is pending verification
                            </p>
                            <p className="text-xs text-amber-600 mt-1">
                                Fill in your shop details and wait for admin approval.
                                Your shop won't be visible to customers until verified.
                            </p>
                        </div>
                        
                           <a href="/dashboard/settings"
                            className="flex-shrink-0 text-xs bg-amber-600 hover:bg-amber-700 text-white px-3 py-1.5 rounded-lg transition-colors"
                        >
                            Complete profile
                        </a>
                    </div>
                )}

                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <h1 className="text-xl font-bold text-gray-900">Incoming Orders</h1>
                        <span className="text-xs text-gray-400">
                            Updated {lastRefresh.toLocaleTimeString()}
                        </span>
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => { playSound(); showBrowserNotification(1) }}
                            className="text-xs text-gray-500 hover:text-gray-700 border border-gray-200 px-3 py-1.5 rounded-lg transition-colors"
                        >
                            Test sound
                        </button>
                        <button
                            onClick={() => fetchOrders(false)}
                            className="text-xs text-green-600 hover:text-green-700 border border-green-200 px-3 py-1.5 rounded-lg transition-colors"
                        >
                            Refresh
                        </button>
                    </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-3 mb-6">
                    <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
                        <p className="text-2xl font-bold text-amber-600">{counts['pending'] || 0}</p>
                        <p className="text-xs text-gray-500 mt-1">Pending</p>
                    </div>
                    <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
                        <p className="text-2xl font-bold text-blue-600">{(counts['confirmed'] || 0) + (counts['preparing'] || 0)}</p>
                        <p className="text-xs text-gray-500 mt-1">In progress</p>
                    </div>
                    <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
                        <p className="text-2xl font-bold text-green-600">{counts['delivered'] || 0}</p>
                        <p className="text-xs text-gray-500 mt-1">Delivered</p>
                    </div>
                </div>

                {/* Filter tabs */}
                <div className="flex gap-2 mb-4 overflow-x-auto">
                    {['pending', 'confirmed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled', 'all'].map((s) => (
                        <button
                            key={s}
                            onClick={() => setFilter(s)}
                            className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                                filter === s
                                    ? 'bg-green-600 text-white'
                                    : 'bg-white border border-gray-200 text-gray-600'
                            }`}
                        >
                            {STATUS_LABELS[s] || 'All'}
                            {counts[s] ? ` (${counts[s]})` : ''}
                        </button>
                    ))}
                </div>

                {/* Orders */}
                {filteredOrders.length === 0 ? (
                    <div className="text-center py-12 text-gray-400">No orders here.</div>
                ) : (
                    <div className="space-y-4">
                        {filteredOrders.map((order) => (
                            <div key={order.id} className="bg-white rounded-xl border border-gray-200 p-5">
                                <div className="flex items-start justify-between mb-3">
                                    <div>
                                        <p className="font-semibold text-gray-900">Order #{order.id}</p>
                                        <p className="text-xs text-gray-500 mt-0.5">
                                            {new Date(order.created_at).toLocaleString()}
                                        </p>
                                    </div>
                                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${STATUS_COLORS[order.status]}`}>
                                        {STATUS_LABELS[order.status]}
                                    </span>
                                </div>

                                <div className="bg-gray-50 rounded-lg p-3 mb-3">
                                    {order.items.map((item) => (
                                        <div key={item.id} className="flex justify-between text-sm py-0.5">
                                            <span className="text-gray-700">
                                                {item.product_name}
                                                {item.cut_type_name && ` (${item.cut_type_name})`}
                                                {' — '}{item.quantity} kg
                                            </span>
                                            <span className="text-gray-900 font-medium">Rs.{item.total_price}</span>
                                        </div>
                                    ))}
                                    <div className="border-t mt-2 pt-2 flex justify-between text-sm font-semibold">
                                        <span>Total</span>
                                        <span>Rs.{order.total_amount}</span>
                                    </div>
                                </div>

                                <div className="text-xs text-gray-500 mb-3 space-y-0.5">
                                    <p>{order.delivery_address.startsWith('PICKUP') ? 'PICKUP' : `Deliver to: ${order.delivery_address}`}</p>
                                    <p>Contact: {order.delivery_name} — {order.delivery_phone}</p>
                                    {order.notes && <p>Note: {order.notes}</p>}
                                </div>

                                <div className="flex gap-2">
                                    {NEXT_STATUS[order.status] && (
                                        <button
                                            onClick={() => handleStatusUpdate(order, NEXT_STATUS[order.status].value)}
                                            disabled={updating[order.id]}
                                            className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-2 rounded-lg transition-colors disabled:opacity-50"
                                        >
                                            {updating[order.id] ? '...' : NEXT_STATUS[order.status].label}
                                        </button>
                                    )}
                                    {['pending', 'confirmed'].includes(order.status) && (
                                        <button
                                            onClick={() => handleCancel(order)}
                                            disabled={updating[order.id]}
                                            className="px-4 bg-red-50 hover:bg-red-100 text-red-600 text-sm font-medium py-2 rounded-lg transition-colors disabled:opacity-50"
                                        >
                                            Cancel
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}