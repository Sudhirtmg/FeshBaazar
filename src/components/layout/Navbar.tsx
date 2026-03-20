// // src/components/layout/Navbar.tsx
// 'use client'
// import { useEffect, useState } from 'react'
// import { useRouter, usePathname } from 'next/navigation'
// import Cookies from 'js-cookie'
// import useAuthStore from '@/store/authStore'
// import { authService } from '@/services/authService'
// import { shopService } from '@/services/shopService'

// export default function Navbar() {
//     const router   = useRouter()
//     const pathname = usePathname()
//     const { user, setUser, logout, isAuthenticated } = useAuthStore()
//     const [menuOpen, setMenuOpen] = useState(false)

//     useEffect(() => {
//         const loadUser = async () => {
//             const token = Cookies.get('access_token')
//             if (token && !user) {
//                 try {
//                     const data = await authService.me()
//                     setUser(data)
//                     if (data.role === 'shop_owner') {
//                         try {
//                             await shopService.getMyShop()
//                         } catch {
//                             router.push('/dashboard/create-shop')
//                         }
//                     }
//                 } catch {
//                     logout()
//                 }
//             }
//         }
//         loadUser()
//     }, [])

//     const handleLogout = () => {
//         logout()
//         router.push('/login')
//     }

//     const isShopOwner = user?.role === 'shop_owner'

//     return (
//         <nav className="bg-white border-b border-gray-200 px-4 py-3 sticky top-0 z-50">
//             <div className="max-w-4xl mx-auto flex items-center justify-between">
//                 <a href={isShopOwner ? '/dashboard' : '/shops'} className="flex items-center gap-2">
//                     <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
//                         <span className="text-white text-sm font-bold">F</span>
//                     </div>
//                     <span className="font-bold text-gray-900">FreshBazaar</span>
//                 </a>

//                 <div className="hidden md:flex items-center gap-6">
//                     {isAuthenticated && !isShopOwner && (
//                         <div className="flex items-center gap-6">
//                             <a href="/shops" className={`text-sm transition-colors ${pathname === '/shops' ? 'text-green-600 font-medium' : 'text-gray-600 hover:text-gray-900'}`}>
//                                 Shops
//                             </a>
//                             <a href="/orders" className={`text-sm transition-colors ${pathname.startsWith('/orders') ? 'text-green-600 font-medium' : 'text-gray-600 hover:text-gray-900'}`}>
//                                 My Orders
//                             </a>
//                             <a href="/cart" className={`text-sm transition-colors ${pathname === '/cart' ? 'text-green-600 font-medium' : 'text-gray-600 hover:text-gray-900'}`}>
//                                 Cart
//                             </a>
//                         </div>
//                     )}

//                     {isAuthenticated && isShopOwner && (
//                         <div className="flex items-center gap-6">
//                             <a href="/dashboard" className={`text-sm transition-colors ${pathname === '/dashboard' ? 'text-green-600 font-medium' : 'text-gray-600 hover:text-gray-900'}`}>
//                                 Orders
//                             </a>
//                             <a href="/dashboard/products" className={`text-sm transition-colors ${pathname.startsWith('/dashboard/products') ? 'text-green-600 font-medium' : 'text-gray-600 hover:text-gray-900'}`}>
//                                 Products
//                             </a>
//                             <a href="/dashboard/settings" className={`text-sm transition-colors ${pathname.startsWith('/dashboard/settings') ? 'text-green-600 font-medium' : 'text-gray-600 hover:text-gray-900'}`}>
//                                 Settings
//                             </a>
//                             <a href="/shops" className="text-sm text-gray-600 hover:text-gray-900">
//                                 Customer view
//                             </a>
//                         </div>
//                     )}

//                     {isAuthenticated ? (
//                         <div className="flex items-center gap-3">
//                             <span className="text-xs text-gray-400">{user?.phone}</span>
//                             <button onClick={handleLogout} className="text-sm text-red-500 hover:text-red-700 transition-colors">
//                                 Logout
//                             </button>
//                         </div>
//                     ) : (
//                         <div className="flex items-center gap-3">
//                             <a href="/login" className="text-sm text-gray-600 hover:text-gray-900">Login</a>
//                             <a href="/register" className="text-sm bg-green-600 hover:bg-green-700 text-white px-4 py-1.5 rounded-lg transition-colors">
//                                 Register
//                             </a>
//                         </div>
//                     )}
//                 </div>

//                 <button onClick={() => setMenuOpen(!menuOpen)} className="md:hidden text-gray-600 hover:text-gray-900">
//                     <div className="space-y-1">
//                         <span className={`block w-6 h-0.5 bg-current transition-transform ${menuOpen ? 'rotate-45 translate-y-1.5' : ''}`} />
//                         <span className={`block w-6 h-0.5 bg-current transition-opacity ${menuOpen ? 'opacity-0' : ''}`} />
//                         <span className={`block w-6 h-0.5 bg-current transition-transform ${menuOpen ? '-rotate-45 -translate-y-1.5' : ''}`} />
//                     </div>
//                 </button>
//             </div>

//             {menuOpen && (
//                 <div className="md:hidden mt-3 pb-3 border-t border-gray-100 pt-3 space-y-2">
//                     {isAuthenticated && !isShopOwner && (
//                         <>
//                             <a href="/shops" className="block text-sm text-gray-700 py-1.5">Shops</a>
//                             <a href="/orders" className="block text-sm text-gray-700 py-1.5">My Orders</a>
//                             <a href="/cart" className="block text-sm text-gray-700 py-1.5">Cart</a>
//                         </>
//                     )}
//                     {isAuthenticated && isShopOwner && (
//                         <>
//                             <a href="/dashboard" className="block text-sm text-gray-700 py-1.5">Orders</a>
//                             <a href="/dashboard/products" className="block text-sm text-gray-700 py-1.5">Products</a>
//                             <a href="/dashboard/settings" className="block text-sm text-gray-700 py-1.5">Settings</a>
//                             <a href="/shops" className="block text-sm text-gray-700 py-1.5">Customer view</a>
//                         </>
//                     )}
//                     {isAuthenticated ? (
//                         <>
//                             <p className="text-xs text-gray-400 py-1">{user?.phone}</p>
//                             <button onClick={handleLogout} className="block text-sm text-red-500 py-1.5">Logout</button>
//                         </>
//                     ) : (
//                         <>
//                             <a href="/login" className="block text-sm text-gray-700 py-1.5">Login</a>
//                             <a href="/register" className="block text-sm text-gray-700 py-1.5">Register</a>
//                         </>
//                     )}
//                 </div>
//             )}
//         </nav>
//     )
// }

// src/components/layout/Navbar.tsx
'use client'
import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Cookies from 'js-cookie'
import useAuthStore from '@/store/authStore'
import { authService } from '@/services/authService'
import { shopService } from '@/services/shopService'

export default function Navbar() {
    const router   = useRouter()
    const pathname = usePathname()
    const { user, setUser, logout, isAuthenticated } = useAuthStore()
    const [menuOpen, setMenuOpen]         = useState(false)
    const [upgrading, setUpgrading]       = useState(false)
    const [showUpgradeModal, setShowUpgradeModal] = useState(false)

    useEffect(() => {
        const loadUser = async () => {
            const token = Cookies.get('access_token')
            if (token && !user) {
                try {
                    const data = await authService.me()
                    setUser(data)
                    if (data.role === 'shop_owner') {
                        try {
                            await shopService.getMyShop()
                        } catch {
                            router.push('/dashboard/create-shop')
                        }
                    }
                } catch {
                    logout()
                }
            }
        }
        loadUser()
    }, [])

    const handleLogout = () => {
        logout()
        router.push('/login')
    }

    const handleBecomeShopOwner = async () => {
        setUpgrading(true)
        try {
            await shopService.becomeShopOwner()
            // Refresh user data to get updated role
            const data = await authService.me()
            setUser(data)
            setShowUpgradeModal(false)
            router.push('/dashboard/settings')
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Failed to upgrade account.')
        } finally {
            setUpgrading(false)
        }
    }

    const isShopOwner = user?.role === 'shop_owner'

    return (
        <>
            <nav className="bg-white border-b border-gray-200 px-4 py-3 sticky top-0 z-50">
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <a href={isShopOwner ? '/dashboard' : '/shops'} className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                            <span className="text-white text-sm font-bold">F</span>
                        </div>
                        <span className="font-bold text-gray-900">FreshBazaar</span>
                    </a>

                    <div className="hidden md:flex items-center gap-6">
                        {isAuthenticated && !isShopOwner && (
                            <div className="flex items-center gap-6">
                                <a href="/shops" className={`text-sm transition-colors ${pathname === '/shops' ? 'text-green-600 font-medium' : 'text-gray-600 hover:text-gray-900'}`}>
                                    Shops
                                </a>
                                <a href="/orders" className={`text-sm transition-colors ${pathname.startsWith('/orders') ? 'text-green-600 font-medium' : 'text-gray-600 hover:text-gray-900'}`}>
                                    My Orders
                                </a>
                                <a href="/cart" className={`text-sm transition-colors ${pathname === '/cart' ? 'text-green-600 font-medium' : 'text-gray-600 hover:text-gray-900'}`}>
                                    Cart
                                </a>
                                {/* ✅ Become a shop owner button for customers */}
                                <button
                                    onClick={() => setShowUpgradeModal(true)}
                                    className="text-sm text-green-600 hover:text-green-700 border border-green-200 hover:border-green-400 px-3 py-1.5 rounded-lg transition-colors"
                                >
                                    Become a shop owner
                                </button>
                            </div>
                        )}

                        {isAuthenticated && isShopOwner && (
                            <div className="flex items-center gap-6">
                                <a href="/dashboard" className={`text-sm transition-colors ${pathname === '/dashboard' ? 'text-green-600 font-medium' : 'text-gray-600 hover:text-gray-900'}`}>
                                    Orders
                                </a>
                                <a href="/dashboard/products" className={`text-sm transition-colors ${pathname.startsWith('/dashboard/products') ? 'text-green-600 font-medium' : 'text-gray-600 hover:text-gray-900'}`}>
                                    Products
                                </a>
                                <a href="/dashboard/settings" className={`text-sm transition-colors ${pathname.startsWith('/dashboard/settings') ? 'text-green-600 font-medium' : 'text-gray-600 hover:text-gray-900'}`}>
                                    Settings
                                </a>
                                <a href="/shops" className="text-sm text-gray-600 hover:text-gray-900">
                                    Customer view
                                </a>
                            </div>
                        )}

                        {isAuthenticated ? (
                            <div className="flex items-center gap-3">
                                <span className="text-xs text-gray-400">{user?.phone}</span>
                                <button onClick={handleLogout} className="text-sm text-red-500 hover:text-red-700 transition-colors">
                                    Logout
                                </button>
                            </div>
                        ) : (
                            <div className="flex items-center gap-3">
                                <a href="/login" className="text-sm text-gray-600 hover:text-gray-900">Login</a>
                                <a href="/register" className="text-sm bg-green-600 hover:bg-green-700 text-white px-4 py-1.5 rounded-lg transition-colors">
                                    Register
                                </a>
                            </div>
                        )}
                    </div>

                    <button onClick={() => setMenuOpen(!menuOpen)} className="md:hidden text-gray-600 hover:text-gray-900">
                        <div className="space-y-1">
                            <span className={`block w-6 h-0.5 bg-current transition-transform ${menuOpen ? 'rotate-45 translate-y-1.5' : ''}`} />
                            <span className={`block w-6 h-0.5 bg-current transition-opacity ${menuOpen ? 'opacity-0' : ''}`} />
                            <span className={`block w-6 h-0.5 bg-current transition-transform ${menuOpen ? '-rotate-45 -translate-y-1.5' : ''}`} />
                        </div>
                    </button>
                </div>

                {/* Mobile menu */}
                {menuOpen && (
                    <div className="md:hidden mt-3 pb-3 border-t border-gray-100 pt-3 space-y-2">
                        {isAuthenticated && !isShopOwner && (
                            <>
                                <a href="/shops" className="block text-sm text-gray-700 py-1.5">Shops</a>
                                <a href="/orders" className="block text-sm text-gray-700 py-1.5">My Orders</a>
                                <a href="/cart" className="block text-sm text-gray-700 py-1.5">Cart</a>
                                {/* ✅ Mobile — become a shop owner */}
                                <button
                                    onClick={() => { setMenuOpen(false); setShowUpgradeModal(true) }}
                                    className="block text-sm text-green-600 py-1.5 text-left w-full"
                                >
                                    Become a shop owner
                                </button>
                            </>
                        )}
                        {isAuthenticated && isShopOwner && (
                            <>
                                <a href="/dashboard" className="block text-sm text-gray-700 py-1.5">Orders</a>
                                <a href="/dashboard/products" className="block text-sm text-gray-700 py-1.5">Products</a>
                                <a href="/dashboard/settings" className="block text-sm text-gray-700 py-1.5">Settings</a>
                                <a href="/shops" className="block text-sm text-gray-700 py-1.5">Customer view</a>
                            </>
                        )}
                        {isAuthenticated ? (
                            <>
                                <p className="text-xs text-gray-400 py-1">{user?.phone}</p>
                                <button onClick={handleLogout} className="block text-sm text-red-500 py-1.5">Logout</button>
                            </>
                        ) : (
                            <>
                                <a href="/login" className="block text-sm text-gray-700 py-1.5">Login</a>
                                <a href="/register" className="block text-sm text-gray-700 py-1.5">Register</a>
                            </>
                        )}
                    </div>
                )}
            </nav>

            {/* ✅ Become a shop owner confirmation modal */}
            {showUpgradeModal && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 px-4"
                    onClick={() => setShowUpgradeModal(false)}
                >
                    <div
                        className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-xl"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h2 className="text-lg font-bold text-gray-900 mb-2">
                            Become a shop owner
                        </h2>
                        <p className="text-sm text-gray-600 mb-4">
                            Your account will be upgraded to a shop owner account.
                            You'll need to fill in your shop details and wait for
                            admin verification before your shop goes live.
                        </p>

                        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-5">
                            <p className="text-xs text-amber-700">
                                Once upgraded, you'll be redirected to the shop
                                dashboard. You can still browse as a customer from
                                the "Customer view" link in the navbar.
                            </p>
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={() => setShowUpgradeModal(false)}
                                className="flex-1 border border-gray-200 text-gray-600 text-sm font-medium py-2.5 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleBecomeShopOwner}
                                disabled={upgrading}
                                className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-2.5 rounded-lg transition-colors disabled:opacity-50"
                            >
                                {upgrading ? 'Upgrading...' : 'Yes, upgrade my account'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}