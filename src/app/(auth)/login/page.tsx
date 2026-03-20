'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Cookies from 'js-cookie'
import useAuthStore from '@/store/authStore'
import { authService } from '@/services/authService'

export default function LoginPage() {
    const router  = useRouter()
    const setUser = useAuthStore((state) => state.setUser)

    const [form, setForm]       = useState({ phone: '', password: '' })
    const [error, setError]     = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        try {
            const res = await authService.login(form.phone, form.password)
            Cookies.set('access_token',  res.tokens.access,  { expires: 1 })
            Cookies.set('refresh_token', res.tokens.refresh, { expires: 30 })
            setUser(res.user)
            if (res.user.role === 'shop_owner') {
                router.push('/dashboard')
            } else {
                router.push('/shops')
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Invalid phone or password.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 w-full max-w-md p-8">
                <div className="mb-8">
                    <div className="flex items-center gap-2 mb-2">
                        <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                            <span className="text-white text-sm font-bold">F</span>
                        </div>
                        <h1 className="text-xl font-bold text-gray-900">FreshBazaar</h1>
                    </div>
                    <p className="text-gray-500 text-sm">Sign in to your account</p>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Phone number
                        </label>
                        <input
                            type="text"
                            value={form.phone}
                            onChange={(e) => setForm({ ...form, phone: e.target.value })}
                            placeholder="+9779800000001"
                            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Password
                        </label>
                        <input
                            type="password"
                            value={form.password}
                            onChange={(e) => setForm({ ...form, password: e.target.value })}
                            placeholder="••••••••"
                            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Signing in...' : 'Sign in'}
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-gray-500">
                    Don't have an account?{' '}
                    <a href="/register" className="text-green-600 font-medium hover:underline">
                        Register
                    </a>
                </p>
            </div>
        </div>
    )
}