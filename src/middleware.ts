import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const protectedRoutes = ['/cart', '/checkout', '/orders', '/dashboard']
const authRoutes      = ['/login', '/register']

export function middleware(request: NextRequest) {
    const token   = request.cookies.get('access_token')?.value
    const path    = request.nextUrl.pathname

    const isProtected = protectedRoutes.some(r => path.startsWith(r))
    const isAuthRoute = authRoutes.some(r => path.startsWith(r))

    if (isProtected && !token) {
        return NextResponse.redirect(new URL('/login', request.url))
    }

    if (isAuthRoute && token) {
        return NextResponse.redirect(new URL('/shops', request.url))
    }

    return NextResponse.next()
}

export const config = {
    matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}