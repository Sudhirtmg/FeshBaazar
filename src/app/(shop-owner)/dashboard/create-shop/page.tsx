'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { shopService } from '@/services/shopService'
import useAuthStore from '@/store/authStore'

export default function CreateShopPage() {
    const router  = useRouter()
    const { user } = useAuthStore()
    const [form, setForm] = useState({
        name:        '',
        phone:       '',
        address:     '',
        city:        '',
        description: '',
    })
    const [loading, setLoading] = useState(false)
    const [checking, setChecking] = useState(true)
    const [error, setError]     = useState('')

    useEffect(() => {
        // if shop owner already has a shop, redirect to dashboard
        const checkShop = async () => {
            try {
                const shop = await shopService.getMyShop()
                if (shop) router.push('/dashboard')
            } catch {
                // no shop yet — show the form
            } finally {
                setChecking(false)
            }
        }
        checkShop()
    }, [])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        try {
            await shopService.createShop(form)
            router.push('/dashboard')
        } catch (err: any) {
            const data = err.response?.data
            if (data?.name)    setError(data.name[0])
            else if (data?.phone)   setError(data.phone[0])
            else if (data?.address) setError(data.address[0])
            else if (data?.city)    setError(data.city[0])
            else setError('Failed to create shop. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    if (checking) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">Loading...</div>

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-2xl mx-auto px-4 py-12">
                <div className="text-center mb-8">
                    <div className="w-12 h-12 bg-green-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <span className="text-white text-xl font-bold">F</span>
                    </div>
                    <h1 className="text-2xl font-bold text-gray-900">Set up your shop</h1>
                    <p className="text-gray-500 text-sm mt-2">
                        Welcome, {user?.phone}! Tell us about your meat shop.
                    </p>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Shop name <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            value={form.name}
                            onChange={(e) => setForm({ ...form, name: e.target.value })}
                            placeholder="e.g. Ram's Meat Shop"
                            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Shop phone <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            value={form.phone}
                            onChange={(e) => setForm({ ...form, phone: e.target.value })}
                            placeholder="+9779800000000"
                            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            City <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            value={form.city}
                            onChange={(e) => setForm({ ...form, city: e.target.value })}
                            placeholder="e.g. Kathmandu"
                            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Address <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            value={form.address}
                            onChange={(e) => setForm({ ...form, address: e.target.value })}
                            placeholder="e.g. Kathmandu-10, Baneshwor"
                            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Description <span className="text-gray-400 font-normal">(optional)</span>
                        </label>
                        <textarea
                            value={form.description}
                            onChange={(e) => setForm({ ...form, description: e.target.value })}
                            placeholder="Tell customers about your shop..."
                            rows={3}
                            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 rounded-xl transition-colors disabled:opacity-50 text-sm"
                    >
                        {loading ? 'Creating shop...' : 'Create my shop'}
                    </button>
                </form>

                <p className="text-center text-xs text-gray-400 mt-4">
                    Your shop will be reviewed before appearing in search results.
                </p>
            </div>
        </div>
    )
}