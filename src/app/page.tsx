import { redirect } from 'next/navigation'
import { cookies } from 'next/headers'

export default async function HomePage() {
    const cookieStore = await cookies()
    const token = cookieStore.get('access_token')
    if (token) redirect('/shops')

    return (
        <div className="min-h-screen bg-white">

            {/* Hero */}
            <div className="relative overflow-hidden bg-gradient-to-br from-green-50 to-white">
                <div className="max-w-4xl mx-auto px-4 py-24 text-center">
                    <div className="inline-flex items-center gap-2 bg-white border border-green-200 text-green-700 text-xs font-medium px-4 py-2 rounded-full mb-8 shadow-sm">
                        <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
                        Now available in Kathmandu
                    </div>
                    <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight tracking-tight">
                        Fresh meat,<br />
                        <span className="text-green-600">delivered fast</span>
                    </h1>
                    <p className="text-xl text-gray-500 mb-10 max-w-lg mx-auto leading-relaxed">
                        Order from verified local butcher shops. Choose your cut, pick your quantity, get it delivered or pick up yourself.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
                        <a href="/register" className="w-full sm:w-auto bg-green-600 hover:bg-green-700 text-white font-semibold px-8 py-4 rounded-2xl transition-colors text-sm shadow-lg shadow-green-200">
                            Order now — it's free
                        </a>
                        <a href="/login" className="w-full sm:w-auto bg-white border-2 border-gray-200 hover:border-gray-300 text-gray-700 font-semibold px-8 py-4 rounded-2xl transition-colors text-sm">
                            Sign in
                        </a>
                    </div>
                    <p className="text-xs text-gray-400 mt-4">No credit card required</p>
                </div>
            </div>

            {/* How it works */}
            <div className="max-w-4xl mx-auto px-4 py-20">
                <p className="text-center text-xs font-semibold text-green-600 uppercase tracking-widest mb-3">How it works</p>
                <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">Order in 3 simple steps</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div className="relative">
                        <div className="w-10 h-10 bg-green-600 text-white rounded-2xl flex items-center justify-center font-bold text-sm mb-4">1</div>
                        <h3 className="font-semibold text-gray-900 mb-2 text-lg">Browse shops</h3>
                        <p className="text-gray-500 text-sm leading-relaxed">Find verified meat shops near you. See what's fresh, check prices and cut types.</p>
                    </div>
                    <div className="relative">
                        <div className="w-10 h-10 bg-green-600 text-white rounded-2xl flex items-center justify-center font-bold text-sm mb-4">2</div>
                        <h3 className="font-semibold text-gray-900 mb-2 text-lg">Add to cart</h3>
                        <p className="text-gray-500 text-sm leading-relaxed">Order by weight (1 kg) or by amount (Rs. 200 worth). Select your preferred cut type.</p>
                    </div>
                    <div className="relative">
                        <div className="w-10 h-10 bg-green-600 text-white rounded-2xl flex items-center justify-center font-bold text-sm mb-4">3</div>
                        <h3 className="font-semibold text-gray-900 mb-2 text-lg">Receive your order</h3>
                        <p className="text-gray-500 text-sm leading-relaxed">Get it delivered to your door or pick up from the shop. Pay cash on delivery.</p>
                    </div>
                </div>
            </div>

            {/* Features */}
            <div className="bg-gray-50 py-20">
                <div className="max-w-4xl mx-auto px-4">
                    <p className="text-center text-xs font-semibold text-green-600 uppercase tracking-widest mb-3">Why FreshBazaar</p>
                    <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">Built for Nepal</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-white rounded-2xl p-6 border border-gray-100">
                            <div className="w-10 h-10 bg-green-50 rounded-xl flex items-center justify-center mb-4">
                                <span className="text-xl">⚖️</span>
                            </div>
                            <h3 className="font-semibold text-gray-900 mb-2">Order by weight or amount</h3>
                            <p className="text-sm text-gray-500 leading-relaxed">Say "1 kg chicken" or "Rs. 500 worth of goat meat" — we handle both.</p>
                        </div>
                        <div className="bg-white rounded-2xl p-6 border border-gray-100">
                            <div className="w-10 h-10 bg-green-50 rounded-xl flex items-center justify-center mb-4">
                                <span className="text-xl">🔪</span>
                            </div>
                            <h3 className="font-semibold text-gray-900 mb-2">Choose your cut</h3>
                            <p className="text-sm text-gray-500 leading-relaxed">Curry cut, boneless, small pieces — specify exactly how you want your meat prepared.</p>
                        </div>
                        <div className="bg-white rounded-2xl p-6 border border-gray-100">
                            <div className="w-10 h-10 bg-green-50 rounded-xl flex items-center justify-center mb-4">
                                <span className="text-xl">🛵</span>
                            </div>
                            <h3 className="font-semibold text-gray-900 mb-2">Delivery or pickup</h3>
                            <p className="text-sm text-gray-500 leading-relaxed">Some shops deliver, some don't. You'll always know before you order.</p>
                        </div>
                        <div className="bg-white rounded-2xl p-6 border border-gray-100">
                            <div className="w-10 h-10 bg-green-50 rounded-xl flex items-center justify-center mb-4">
                                <span className="text-xl">💵</span>
                            </div>
                            <h3 className="font-semibold text-gray-900 mb-2">Cash on delivery</h3>
                            <p className="text-sm text-gray-500 leading-relaxed">Pay when your order arrives. No online payment required.</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Shop owner CTA */}
            <div className="max-w-4xl mx-auto px-4 py-20">
                <div className="bg-green-600 rounded-3xl p-10 text-center text-white">
                    <h2 className="text-3xl font-bold mb-3">Own a meat shop?</h2>
                    <p className="text-green-100 mb-8 text-sm max-w-md mx-auto leading-relaxed">
                        Join FreshBazaar and reach more customers in Kathmandu. Manage orders, set your delivery options, and grow your business.
                    </p>
                    <a href="/register" className="inline-block bg-white text-green-600 hover:bg-green-50 font-semibold px-8 py-4 rounded-2xl transition-colors text-sm">
                        Register your shop — free
                    </a>
                </div>
            </div>

            {/* Footer */}
            <div className="border-t border-gray-100 py-8">
                <div className="max-w-4xl mx-auto px-4 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-7 h-7 bg-green-600 rounded-lg flex items-center justify-center">
                            <span className="text-white text-xs font-bold">F</span>
                        </div>
                        <span className="font-bold text-gray-900 text-sm">FreshBazaar</span>
                    </div>
                    <p className="text-xs text-gray-400">© 2026 FreshBazaar. Made in Nepal.</p>
                </div>
            </div>

        </div>
    )
}