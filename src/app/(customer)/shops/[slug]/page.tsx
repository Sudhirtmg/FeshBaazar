'use client'
import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { shopService } from '@/services/shopService'
import { productService } from '@/services/productService'
import { cartService } from '@/services/cartService'
import { Shop, Product } from '@/types'
import Cookies from 'js-cookie'

export default function ShopDetailPage() {
    const params = useParams()
    const router = useRouter()
    const slug   = params.slug as string

    const [shop, setShop]         = useState<Shop | null>(null)
    const [products, setProducts] = useState<Product[]>([])
    const [loading, setLoading]   = useState(true)
    const [adding, setAdding]     = useState<{ [id: number]: boolean }>({})
    const [selectedCut, setSelectedCut] = useState<{ [id: number]: number | null }>({})
    const [quantities, setQuantities]   = useState<{ [id: number]: string }>({})
    const [amounts, setAmounts]         = useState<{ [id: number]: string }>({})
    const [orderMode, setOrderMode]     = useState<{ [id: number]: 'weight' | 'amount' }>({})
    const [feedback, setFeedback]       = useState<{ [id: number]: string }>({})

    useEffect(() => {
        const fetchData = async () => {
            try {
                const shopData = await shopService.getShop(slug)
                setShop(shopData)
                const shopProducts = await productService.getProducts({ shop: shopData.id })
                setProducts(shopProducts)
                const initQty: { [k: number]: string } = {}
                const initAmt: { [k: number]: string } = {}
                shopProducts.forEach(p => { initQty[p.id] = '1'; initAmt[p.id] = '100' })
                setQuantities(initQty)
                setAmounts(initAmt)
            } catch (err) {
                console.error(err)
            } finally {
                setLoading(false)
            }
        }
        fetchData()
    }, [slug])

    const handleAddToCart = async (product: Product) => {
        const token = Cookies.get('access_token')
        if (!token) {
            router.push('/login?next=/shops/' + slug)
            return
        }
        setAdding(prev => ({ ...prev, [product.id]: true }))
        const mode = orderMode[product.id] || 'weight'
        try {
            await cartService.addItem({
                product:  product.id,
                cut_type: selectedCut[product.id] ?? undefined,
                quantity: mode === 'weight' ? parseFloat(quantities[product.id] || '1') : undefined,
                amount:   mode === 'amount' ? parseFloat(amounts[product.id] || '100') : undefined,
            })
            setFeedback(prev => ({ ...prev, [product.id]: 'Added!' }))
            setTimeout(() => setFeedback(prev => ({ ...prev, [product.id]: '' })), 2000)
        } catch (err: any) {
            if (err.response?.status === 401) router.push('/login?next=/shops/' + slug)
            else setFeedback(prev => ({ ...prev, [product.id]: 'Failed.' }))
        } finally {
            setAdding(prev => ({ ...prev, [product.id]: false }))
        }
    }

    if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">Loading...</div>
    if (!shop)   return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">Shop not found.</div>

    const isLoggedIn = !!Cookies.get('access_token')

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-4xl mx-auto px-4 py-6">
                <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6">
                    <div className="flex items-start justify-between">
                        <div>
                            <h1 className="text-xl font-bold text-gray-900">{shop.name}</h1>
                            <p className="text-gray-500 text-sm mt-1">{shop.address}, {shop.city}</p>
                            <p className="text-gray-500 text-sm">{shop.phone}</p>
                        </div>
                        <span className={`text-xs font-medium px-3 py-1 rounded-full ${shop.is_open ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'}`}>
                            {shop.is_open ? 'Open' : 'Closed'}
                        </span>
                    </div>
                </div>

                <h2 className="text-lg font-semibold text-gray-900 mb-4">Products</h2>

                {products.length === 0 ? (
                    <div className="text-center py-12 text-gray-400">No products available.</div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {products.map((product) => (
                            <div key={product.id} className="bg-white rounded-xl border border-gray-200 p-5">
                                <div className="flex items-start justify-between mb-2">
                                    <h3 className="font-semibold text-gray-900">{product.name}</h3>
                                    <span className="text-green-700 font-bold text-sm">
                                        Rs.{product.effective_price}/{product.unit}
                                    </span>
                                </div>
                                <p className="text-xs text-gray-500 mb-3">
                                    Stock: {product.stock_quantity} {product.unit} available
                                </p>

                                {product.cut_types.length > 0 && (
                                    <div className="mb-3">
                                        <p className="text-xs text-gray-500 mb-1">Select cut:</p>
                                        <div className="flex flex-wrap gap-1">
                                            <button
                                                type="button"
                                                onClick={() => setSelectedCut(prev => ({ ...prev, [product.id]: null }))}
                                                className={`text-xs px-2 py-1 rounded-full border transition-colors ${!selectedCut[product.id] ? 'bg-green-600 text-white border-green-600' : 'bg-white text-gray-600 border-gray-300'}`}
                                            >
                                                No preference
                                            </button>
                                            {product.cut_types.map((cut) => (
                                                <button
                                                    key={cut.id}
                                                    type="button"
                                                    onClick={() => setSelectedCut(prev => ({ ...prev, [product.id]: cut.id }))}
                                                    className={`text-xs px-2 py-1 rounded-full border transition-colors ${selectedCut[product.id] === cut.id ? 'bg-green-600 text-white border-green-600' : 'bg-white text-gray-600 border-gray-300'}`}
                                                >
                                                    {cut.name} {cut.extra_price !== '0.00' && `+Rs.${cut.extra_price}`}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <div className="mb-3">
                                    <div className="flex rounded-lg border border-gray-300 overflow-hidden text-xs">
                                        <button
                                            type="button"
                                            onClick={() => setOrderMode(prev => ({ ...prev, [product.id]: 'weight' }))}
                                            className={`flex-1 py-1.5 font-medium transition-colors ${(orderMode[product.id] || 'weight') === 'weight' ? 'bg-green-600 text-white' : 'bg-white text-gray-600'}`}
                                        >
                                            By weight (kg)
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => setOrderMode(prev => ({ ...prev, [product.id]: 'amount' }))}
                                            className={`flex-1 py-1.5 font-medium transition-colors ${orderMode[product.id] === 'amount' ? 'bg-green-600 text-white' : 'bg-white text-gray-600'}`}
                                        >
                                            By amount (Rs.)
                                        </button>
                                    </div>
                                </div>

                                {(orderMode[product.id] || 'weight') === 'weight' ? (
                                    <div className="flex items-center gap-2 mb-3">
                                        <label className="text-xs text-gray-500">Qty (kg):</label>
                                        <input
                                            type="number"
                                            min="0.1"
                                            step="0.1"
                                            max={parseFloat(product.stock_quantity)}
                                            value={quantities[product.id]}
                                            onChange={(e) => {
                                                const raw = e.target.value
                                                const val = parseFloat(raw)
                                                const max = parseFloat(product.stock_quantity)
                                                if (raw === '' || raw === '0') {
                                                    setQuantities(prev => ({ ...prev, [product.id]: '' }))
                                                } else if (!isNaN(val) && val > max) {
                                                    setQuantities(prev => ({ ...prev, [product.id]: product.stock_quantity }))
                                                } else {
                                                    setQuantities(prev => ({ ...prev, [product.id]: raw }))
                                                }
                                            }}
                                            placeholder="e.g. 1.5"
                                            className="w-24 border border-gray-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                        />
                                        <span className="text-xs text-gray-400">
                                            ≈ Rs.{(parseFloat(quantities[product.id] || '0') * parseFloat(product.effective_price)).toFixed(0)}
                                        </span>
                                    </div>
                                ) : (
                                    <div className="flex items-center gap-2 mb-3">
                                        <label className="text-xs text-gray-500">Amount (Rs.):</label>
                                        <input
                                            type="number"
                                            min="10"
                                            step="10"
                                            max={parseFloat(product.stock_quantity) * parseFloat(product.effective_price)}
                                            value={amounts[product.id]}
                                            onChange={(e) => {
                                                const raw    = e.target.value
                                                const val    = parseFloat(raw)
                                                const maxAmt = parseFloat(product.stock_quantity) * parseFloat(product.effective_price)
                                                if (raw === '' || raw === '0') {
                                                    setAmounts(prev => ({ ...prev, [product.id]: '' }))
                                                } else if (!isNaN(val) && val > maxAmt) {
                                                    setAmounts(prev => ({ ...prev, [product.id]: maxAmt.toFixed(0) }))
                                                } else {
                                                    setAmounts(prev => ({ ...prev, [product.id]: raw }))
                                                }
                                            }}
                                            placeholder="e.g. 200"
                                            className="w-24 border border-gray-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                        />
                                        <span className="text-xs text-gray-400">
                                            ≈ {(parseFloat(amounts[product.id] || '0') / parseFloat(product.effective_price)).toFixed(2)} kg
                                        </span>
                                    </div>
                                )}

                                <button
                                    onClick={() => handleAddToCart(product)}
                                    disabled={adding[product.id]}
                                    className="w-full bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-2 rounded-lg transition-colors disabled:opacity-50"
                                >
                                    {adding[product.id] ? 'Adding...' : feedback[product.id] || (isLoggedIn ? 'Add to cart' : 'Login to order')}
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}