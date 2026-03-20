// src/types/index.ts 
export interface User {
    id: number
    phone: string
    email: string
    role: 'customer' | 'shop_owner' | 'delivery_rider' | 'admin'
    profile_image: string | null
    date_joined: string
}

export interface ShopSchedule {
    id: number
    weekday: number
    weekday_name: string
    is_active: boolean
    morning_open: string | null
    morning_close: string | null
    afternoon_open: string | null
    afternoon_close: string | null
}

export interface Shop {
    id: number
    name: string
    slug: string
    description: string
    phone: string
    address: string
    city: string
    logo: string | null
    is_open: boolean
    is_verified: boolean
    is_temporarily_closed: boolean
    temporary_close_note: string
    next_opening: string | null
    owner_phone: string
    schedules: ShopSchedule[]
    created_at: string
}

export interface CutType {
    id: number
    name: string
    extra_price: string
    is_active: boolean
}

export interface Product {
    id: number
    name: string
    slug: string
    description: string
    price: string
    discount_price: string | null
    effective_price: string
    stock_quantity: string
    unit: string
    image: string | null
    is_available: boolean
    category: number
    category_name: string
    shop: number
    shop_name: string
    cut_types: CutType[]
    created_at: string
}

export interface CartItem {
    id: number
    product: number
    product_name: string
    cut_type: number | null
    cut_type_name: string | null
    shop_name: string
    quantity: string
    amount: string
    price_at_time: string
    subtotal: string
}

export interface Cart {
    id: number
    items: CartItem[]
    total: string
    item_count: number
    updated_at: string
}

export interface OrderItem {
    id: number
    product: number
    product_name: string
    cut_type_name: string
    quantity: string
    unit_price: string
    total_price: string
}

export interface Order {
    id: number
    shop: number
    status: string
    payment_method: string
    subtotal: string
    delivery_fee: string
    total_amount: string
    delivery_name: string
    delivery_phone: string
    delivery_address: string
    notes: string
    items: OrderItem[]
    history: OrderStatusHistory[]
    created_at: string
}

export interface OrderStatusHistory {
    from_status: string
    to_status: string
    changed_by_phone: string
    note: string
    created_at: string
}