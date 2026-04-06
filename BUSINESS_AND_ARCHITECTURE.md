# FreshBazaar — Business Strategy & Code Architecture

> A full-stack e-commerce platform for local meat shops and cold storage suppliers in Nepal.

---

## Table of Contents

1. [Business Strategy](#1-business-strategy)
2. [System Architecture](#2-system-architecture)
3. [Backend Architecture](#3-backend-architecture)
4. [Frontend Architecture](#4-frontend-architecture)
5. [Database Schema](#5-database-schema)
6. [API Endpoints](#6-api-endpoints)
7. [Authentication & Authorization](#7-authentication--authorization)
8. [Key Business Flows](#8-key-business-flows)
9. [Deployment](#9-deployment)
10. [Development Setup](#10-development-setup)
11. [Future Roadmap](#11-future-roadmap)

---

## 1. Business Strategy

### 1.1 Vision

FreshBazaar digitizes the meat supply chain in Nepal by connecting:
- **Customers** → who want fresh meat delivered or picked up
- **Meat Shops** → local butchers who sell to end consumers
- **Cold Storage Suppliers** → wholesale meat distributors who supply shops
- **Platform Admin** → manages verification, quality, and ecosystem

### 1.2 Business Model

| Phase | Strategy | Revenue Source |
|-------|----------|---------------|
| **Phase 1** | Single shop MVP (test with one shop) | None — validation |
| **Phase 2** | Multi-shop marketplace | Shop subscription / commission per order |
| **Phase 3** | Delivery layer + riders | Delivery service fee |
| **Phase 4** | B2B wholesale (cold storage → shops) | Supplier listing fee + transaction commission |
| **Phase 5** | Advanced features (analytics, AI demand prediction) | Premium features, featured shops |

### 1.3 Target Market

- **Primary**: Urban Nepal (Kathmandu Valley initially)
- **Secondary**: Other major cities (Pokhara, Chitwan, Biratnagar)
- **Problem Solved**: Unhygienic meat shopping experience, no price transparency, no delivery, no ordering convenience

### 1.4 Competitive Advantage

1. **Cut-type customization** — customers choose how meat is cut (curry, boneless, BBQ, etc.)
2. **B2B supply chain** — shops order wholesale from cold storage through the same platform
3. **Credit/Ledger system** — traditional "udharo" (credit) tracking for B2B transactions
4. **Walk-in shop support** — cold storage can create manual orders for walk-in customers
5. **Staff permission system** — shop owners can delegate specific abilities to staff members

### 1.5 User Roles

| Role | Description | Key Capabilities |
|------|-------------|-----------------|
| `customer` | End consumer | Browse shops, order meat, track orders |
| `shop_owner` | Meat shop proprietor | Manage shop, products, orders, order wholesale from cold storage |
| `cold_storage` | Wholesale meat supplier | Manage products, fulfill B2B orders, manage ledger/credit |
| `staff` | Employee of cold storage | Granular permissions (view orders, collect payments, manage products, etc.) |
| `delivery_rider` | Delivery person | (Reserved for future delivery tracking) |
| `admin` | Platform administrator | Verify shops, manage ecosystem (via Django admin) |

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRESHBAZAAR PLATFORM                   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐         ┌──────────────────────┐   │
│  │   Frontend       │         │      Backend         │   │
│  │   Next.js 14     │◄───────►│   Django REST API    │   │
│  │   (Vercel)       │  HTTPS  │   (Render)           │   │
│  └──────────────────┘         └──────────┬───────────┘   │
│                                          │                │
│                                   ┌──────▼───────┐        │
│                                   │  PostgreSQL   │        │
│                                   │  Database     │        │
│                                   └──────────────┘        │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │              WebSocket (Django Channels)          │    │
│  │         Real-time order & ledger updates          │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 2.1 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 14 (App Router) | SSR/SSG, routing, UI |
| Styling | Tailwind CSS | Utility-first CSS |
| State Management | Zustand | Lightweight global state |
| HTTP Client | Axios + Fetch API | API communication |
| Authentication | JWT (SimpleJWT) | Token-based auth via cookies |
| Backend | Django 5.x + DRF | REST API, business logic |
| Database | PostgreSQL | Relational data storage |
| Real-time | Django Channels (WebSocket) | Live order/ledger updates |
| Media | Local filesystem (dev) / WhiteNoise (prod) | Image uploads |
| Deployment | Vercel (FE) + Render (BE) | Cloud hosting |

### 2.2 Project Structure

```
MEAT_SHOP/
├── Backend/                          # Django REST API
│   ├── config/                       # Django project settings
│   │   ├── settings.py               # Main config (DB, CORS, JWT, etc.)
│   │   ├── urls.py                   # Root URL routing
│   │   ├── asgi.py                   # ASGI config (WebSocket support)
│   │   └── wsgi.py                   # WSGI config (production server)
│   ├── apps/                         # Modular Django apps
│   │   ├── accounts/                 # User management & auth
│   │   ├── shops/                    # Shop profiles & schedules
│   │   ├── products/                 # Product catalog & cut types
│   │   ├── cart/                     # Shopping cart
│   │   ├── orders/                   # Customer orders (B2C)
│   │   ├── deliveries/               # Delivery management
│   │   ├── customers/                # Customer profiles
│   │   ├── notifications/            # Push/in-app notifications
│   │   ├── b2b/                      # B2B wholesale (cold storage ↔ shops)
│   │   └── common/                   # Shared permissions & utilities
│   ├── media/                        # Uploaded images (logos, products)
│   ├── requirements.txt              # Python dependencies
│   ├── Procfile                      # Heroku/Render deployment config
│   └── manage.py                     # Django CLI
│
├── FrontEnd/
│   └── freshbazaar/                  # Next.js 14 application
│       ├── src/
│       │   ├── app/                  # App Router pages
│       │   │   ├── (auth)/           # Login & Register routes
│       │   │   ├── (customer)/       # Customer-facing pages
│       │   │   ├── (shop-owner)/     # Shop owner dashboard
│       │   │   ├── (cold-storage)/   # Cold storage dashboard
│       │   │   └── become-shop-owner/ # Shop onboarding
│       │   ├── components/           # Reusable React components
│       │   ├── services/             # API service layer
│       │   ├── store/                # Zustand state stores
│       │   ├── lib/                  # Utilities (API client, WebSocket)
│       │   ├── hooks/                # Custom React hooks
│       │   ├── types/                # TypeScript type definitions
│       │   └── styles/               # Theme configuration
│       ├── public/                   # Static assets
│       ├── next.config.ts            # Next.js configuration
│       └── package.json              # Node dependencies
│
└── Important Document/               # Business notes & test plans
```

---

## 3. Backend Architecture

### 3.1 App: `accounts` — User Management

**File**: `Backend/apps/accounts/models.py`

Custom user model replacing `username` with `phone` as the primary identifier.

```
User (AbstractUser)
├── phone (unique, login field)
├── email (optional, unique)
├── name
├── role (customer | shop_owner | cold_storage | delivery_rider | staff | admin)
├── profile_image
├── owner (FK → self, for staff hierarchy)
├── can_collect_payment (bool)
├── can_view_ledger (bool)
├── can_create_order (bool)
├── can_manage_products (bool)
├── can_view_orders (bool)
├── can_deliver_orders (bool)
├── can_confirm_orders (bool)
└── StaffActionLog (audit trail)
```

**Key Views**:
- `RegisterView` — POST `/api/auth/register/` — Creates user + auto-creates ColdStorage for cold_storage role
- `LoginView` — POST `/api/auth/login/` — Returns user + JWT tokens
- `MeView` — GET/PATCH `/api/auth/me/` — Get/update current user

**Auth Backend**: `PhoneBackend` — authenticates using phone + password instead of username.

### 3.2 App: `shops` — Shop Management

**File**: `Backend/apps/shops/models.py`

```
Shop
├── owner (FK → User)
├── name, slug (auto-generated with UUID)
├── description, address, city, phone
├── logo (ImageField)
├── is_walkin (bool — for manual walk-in shops)
├── is_verified, verification_status (pending | verified | rejected)
├── rejection_reason
├── has_delivery, delivery_charge
├── is_temporarily_closed, temporary_close_note
├── latitude, longitude
├── @property is_open (computed from schedules)
└── @property next_opening (computed next open time)

ShopSchedule
├── shop (FK → Shop)
├── weekday (0-6)
├── is_active
├── morning_open, morning_close
├── afternoon_open, afternoon_close
└── close_note
```

**Key Logic**:
- `Shop.save()` auto-unverifies when info fields change (name, address, city, phone, description)
- `is_open` property checks current time against active schedules (supports morning + afternoon slots)
- `next_opening` property computes when the shop next opens
- Walk-in shops bypass verification and are auto-verified

**API Endpoints**:
| Method | Path | View | Permission |
|--------|------|------|------------|
| GET | `/api/shops/` | ShopListView | AllowAny (filters: city) |
| GET | `/api/shops/<slug>/` | ShopDetailView | AllowAny |
| GET | `/api/shops/my-shop/` | MyShopView | IsShopOwner |
| PATCH | `/api/shops/onboarding/` | ShopOnboardingView | IsShopOwner |
| POST | `/api/shops/schedule/` | ShopScheduleView | IsShopOwner |
| GET | `/api/shops/schedule/` | ShopScheduleView | IsShopOwner |
| PATCH | `/api/shops/<slug>/update/` | ShopUpdateView | IsOwnerOfShop |
| POST | `/api/shops/create-walkin/` | CreateWalkInShopView | IsAuthenticated |
| POST | `/api/shops/become-shop-owner/` | BecomeShopOwnerView | IsAuthenticated |
| POST | `/api/shops/cancel-owner-request/` | CancelShopOwnerRequestView | IsAuthenticated |

### 3.3 App: `products` — Product Catalog

**File**: `Backend/apps/products/models.py`

```
Category
├── name, slug (auto-generated)
└── created_at

Product
├── shop (FK → Shop)
├── category (FK → Category, nullable)
├── name, slug (unique per shop)
├── description, price, discount_price
├── stock_quantity, unit (kg | piece | pack)
├── image, is_available
├── @property effective_price (returns discount_price if set, else price)
└── created_at, updated_at

CutType
├── product (FK → Product)
├── name (e.g., "curry cut", "boneless", "bbq cut")
├── extra_price (added to base price)
└── is_active
```

**Key Logic**:
- Slug is unique per shop (not globally), allowing same product names across shops
- `effective_price` property handles discount logic
- Cut types allow meat-specific customization with extra pricing

### 3.4 App: `cart` — Shopping Cart

**File**: `Backend/apps/cart/models.py`

```
Cart
├── user (OneToOne → User, one cart per customer)
├── @property total (sum of all item subtotals)
├── @property item_count
└── created_at, updated_at

CartItem
├── cart (FK → Cart)
├── product (FK → Product)
├── cut_type (FK → CutType, nullable)
├── quantity (nullable — derived from amount if not set)
├── amount (nullable — derived from quantity if not set)
├── price_at_time (snapshot at addition)
└── unique_together: (cart, product, cut_type)
```

**Key Logic**:
- Supports dual ordering: by weight (quantity) OR by price (amount)
- Auto-derives quantity from amount and vice versa
- `price_at_time` snapshots price to prevent issues when prices change

### 3.5 App: `b2b` — B2B Wholesale (Cold Storage ↔ Shops)

**File**: `Backend/apps/b2b/models.py`

This is the most complex app, handling wholesale supply chain.

```
ColdStorage
├── owner (OneToOne → User)
├── name, address
├── latitude, longitude
├── verified
└── created_at

ColdStorageProduct
├── cold_storage (FK → ColdStorage)
├── name, category (chicken | beef | buffalo | mutton | pork | seafood | other)
├── price_per_kg, stock_kg
├── min_order_kg, low_stock_threshold
├── unit_type (kg | piece)
├── allowed_units (JSONField — ['kg'], ['piece'], or ['kg','piece'])
├── approx_weight_per_piece_kg (informational)
├── stock_pieces (for piece-based products)
├── is_available
└── created_at, updated_at

B2BOrder
├── shop (FK → Shop)
├── cold_storage (FK → ColdStorage)
├── status (pending_price → priced → pending → confirmed → processing → dispatched → delivered | cancelled)
├── total_price, paid_amount
├── delivery_type (pickup | delivery)
├── delivery_address, delivery_latitude, delivery_longitude
├── payment_type (cash | credit)
├── order_source (app | phone | walkin)
├── created_by (FK → User, nullable — for staff-created orders)
├── notes
├── @property is_paid (total_price <= paid_amount)
├── @property payment_status (paid | partial | unpaid)
├── @property remaining_amount()
├── can_transition_to(new_status) — validates state machine
└── recalculate_total() — recomputes from items

B2BOrderItem
├── order (FK → B2BOrder)
├── product (FK → ColdStorageProduct, PROTECT)
├── product_name_snapshot
├── unit_type (kg | piece)
├── quantity, quantity_kg
├── price_per_kg_snapshot
├── actual_weight_kg (nullable — filled by supplier for piece orders)
├── price_per_kg_final (nullable — set by supplier for piece orders)
├── line_total (nullable — NULL for unpriced piece orders)
└── price (backwards compat)

B2BOrderStatusHistory
├── order (FK → B2BOrder)
├── from_status, to_status
├── changed_by (FK → User)
├── note
└── created_at

LedgerEntry
├── shop (FK → Shop)
├── cold_storage (FK → ColdStorage)
├── order (FK → B2BOrder, nullable)
├── amount, balance_after
├── entry_type (credit | payment)
├── collected_by (FK → User)
├── weighted_by (FK → User — who weighed/priced the order)
├── note
└── created_at
```

**Key Business Logic**:

1. **Piece-based ordering**: Shops can order meat by piece count. The cold storage weighs each piece after receiving the order and sets the final price. This creates a `pending_price` → `priced` workflow.

2. **Credit system (Udharo)**: Shops can order on credit. The `LedgerEntry` model tracks all credits and payments, computing running balances. Credit limit is ₹50,000.

3. **Walk-in orders**: Cold storage staff can create manual orders for walk-in customers using `CreateWalkInShopView`, which auto-verifies the shop.

4. **Staff permissions**: Staff members have granular permissions (`can_view_orders`, `can_collect_payment`, `can_manage_products`, etc.) enforced at both the view and permission level.

5. **State machine**: B2B orders follow strict status transitions:
   ```
   pending_price → priced → confirmed → processing → dispatched → delivered
         ↓              ↓        ↓
      cancelled      cancelled  cancelled
   ```

**B2B API Endpoints**:
| Method | Path | View | Permission |
|--------|------|------|------------|
| GET | `/api/b2b/cold-storages/` | ColdStorageListView | IsShopOwner |
| GET | `/api/b2b/cold-storages/<id>/` | ColdStorageDetailView | IsShopOwner |
| GET | `/api/b2b/my-cold-storage/` | MyColdStorageView | IsColdStorageOrStaff |
| PATCH | `/api/b2b/my-cold-storage/` | MyColdStorageView | IsColdStorageOrStaff |
| GET | `/api/b2b/my-cold-storage/products/` | ColdStorageProductListCreateView | IsColdStorageOrStaff |
| POST | `/api/b2b/my-cold-storage/products/` | ColdStorageProductListCreateView | IsColdStorageOrStaff |
| GET/PATCH/DELETE | `/api/b2b/my-cold-storage/products/<id>/` | ColdStorageProductDetailView | IsColdStorageOrStaff |
| POST | `/api/b2b/orders/` | B2BOrderCreateView | IsShopOwnerOrColdStorage |
| GET | `/api/b2b/orders/my-shop/` | ShopB2BOrderListView | IsShopOwner |
| GET | `/api/b2b/orders/incoming/` | ColdStorageIncomingOrderListView | IsColdStorageOrStaff |
| PATCH | `/api/b2b/orders/<id>/status/` | B2BOrderStatusUpdateView | IsColdStorageOrStaff |
| POST | `/api/b2b/orders/<id>/set-price/` | SetPriceView | IsColdStorageOrStaff |
| PATCH | `/api/b2b/orders/<id>/confirm/` | ShopOrderConfirmView | IsShopOwner |
| GET | `/api/b2b/orders/<id>/` | B2BOrderDetailView | IsColdStorageOrStaff |
| GET | `/api/b2b/reports/daily/` | DailyReportView | IsAuthenticated |
| GET | `/api/b2b/ledger/` | Ledger views | IsColdStorageOrStaff |
| POST | `/api/b2b/ledger/payment/` | Payment views | CanCollectPaymentOnly |
| GET | `/api/map/locations/` | MapLocationsView | IsAuthenticated |

### 3.6 App: `common` — Shared Permissions

**File**: `Backend/apps/common/permissions.py`

| Permission Class | Description |
|-----------------|-------------|
| `IsShopOwner` | User role must be `shop_owner` |
| `IsOwnerOfShop` | User must own the specific shop object |
| `IsColdStorage` | User role must be `cold_storage` |
| `IsShopOwnerOrColdStorage` | Either role allowed |
| `IsColdStorageOrStaff` | Cold storage owner or their staff |
| `CanCollectPaymentOnly` | Owner always allowed; staff only for POST |
| `StaffPermission(permission_name)` | Generic — checks specific staff permission field |

### 3.7 Real-time Communication

**WebSocket** via Django Channels at `/ws/orders/`:
- Channel layer: `InMemoryChannelLayer` (development; should use Redis in production)
- Events: `new_order`, `order_confirmed`, `order_processing`, `delivery_assigned`
- Used for live dashboard updates in cold storage and shop owner panels

**Notification System**:
- In-app notifications stored in database
- Polled every 3 seconds from frontend
- Sound alerts for new orders
- Types: `order_status`, `shop_verified`, `shop_rejected`, `b2b_order_placed`, `b2b_order_updated`

---

## 4. Frontend Architecture

### 4.1 Next.js App Router Structure

```
src/app/
├── layout.tsx                          # Root layout (Navbar + children)
├── page.tsx                            # Landing page
├── (auth)/
│   ├── login/page.tsx                  # Phone + password login
│   └── register/page.tsx              # Registration with role selection
├── (customer)/
│   ├── shops/page.tsx                  # Browse shops (list + map view)
│   ├── shops/[slug]/page.tsx           # Shop detail + product listing
│   ├── cart/page.tsx                   # Shopping cart
│   ├── checkout/page.tsx               # Checkout (delivery/pickup, scheduling)
│   ├── orders/page.tsx                 # Order history
│   └── orders/[id]/page.tsx            # Order detail + tracking
├── (shop-owner)/
│   ├── dashboard/page.tsx              # Incoming orders management
│   ├── dashboard/products/page.tsx     # Product management
│   ├── dashboard/settings/page.tsx     # Shop profile settings
│   ├── cold-storage/page.tsx           # Browse cold storages
│   ├── cold-storage/[id]/page.tsx      # Cold storage detail + bulk order
│   └── b2b-orders/page.tsx             # B2B order history
├── (cold-storage)/
│   ├── cs-dashboard/page.tsx           # Operations dashboard (orders, stats)
│   ├── cs-products/page.tsx            # Product CRUD
│   ├── cs-products/[id]/edit/page.tsx  # Edit product
│   ├── cs-products/new/page.tsx        # New product
│   ├── cs-orders/page.tsx              # Incoming B2B orders
│   ├── ledger/page.tsx                 # Credit/ledger management
│   ├── ledger/[shopId]/page.tsx        # Shop-specific ledger
│   ├── cs-payment/page.tsx             # Payment collection
│   ├── cs-reports/page.tsx             # Daily reports
│   ├── cs-manual-order/page.tsx        # Walk-in order creation
│   ├── staff/page.tsx                  # Staff management
│   ├── cs-dashboard/create-staff/page.tsx  # Create staff member
│   └── staff-dashboard/page.tsx        # Staff-specific dashboard
└── become-shop-owner/page.tsx          # Shop onboarding form
```

### 4.2 Route Groups

The `(auth)`, `(customer)`, `(shop-owner)`, and `(cold-storage)` are **route groups** — they organize pages without affecting URL paths. This allows different layouts and middleware logic per user type.

### 4.3 State Management (Zustand)

**File**: `src/store/authStore.ts`

```typescript
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User) => void;
  logout: () => void;
}
```

Simple global store for auth state. Persists via cookies (`access_token`, `refresh_token`).

### 4.4 API Client Layer

**File**: `src/lib/api.ts`

Axios instance with:
- Base URL from `NEXT_PUBLIC_API_URL` env var
- JWT token auto-injection via request interceptor
- 401 handling: clears tokens and redirects to `/login`

**File**: `src/lib/api/b2b.ts`

Dedicated B2B API client using native `fetch` with:
- Token from cookies
- Error parsing and alert display
- All B2B endpoints (cold storages, orders, ledger, reports)

### 4.5 Service Layer

| Service | File | Purpose |
|---------|------|---------|
| `authService` | `src/services/authService.ts` | Login, register, me |
| `shopService` | `src/services/shopService.ts` | Shop CRUD, become shop owner |
| `productService` | `src/services/productService.ts` | Product CRUD |
| `cartService` | `src/services/cartService.ts` | Cart operations |
| `orderService` | `src/services/orderService.ts` | Checkout, order status updates |

### 4.6 Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `Navbar` | `src/components/layout/Navbar.tsx` | Main navigation, role-based links, notifications, profile menu |
| `BulkOrderForm` | `src/components/b2b/BulkOrderForm.tsx` | B2B order placement with kg/piece selection |
| `OrderStatusBadge` | `src/components/b2b/OrderStatusBadge.tsx` | Status display for B2B orders |
| `BecomeSupplierCard` | `src/components/b2b/BecomeSupplierCard.tsx` | CTA to become a cold storage supplier |
| `ColdStorageCard` | `src/components/b2b/ColdStorageCard.tsx` | Cold storage listing card |
| `ShopsMap` | `src/components/map/ShopsMap.tsx` | Map view of shops |
| `DeliveryRouteMap` | `src/components/map/DeliveryRouteMap.tsx` | Route visualization between shop and cold storage |
| `AuthLoader` | `src/components/AuthLoader.tsx` | Auth state initialization wrapper |

### 4.7 Middleware

**File**: `src/middleware.ts`

Route protection:
- Protected routes (`/cart`, `/checkout`, `/orders`, `/dashboard`) redirect to `/login` if no token
- Auth routes (`/login`, `/register`) redirect to `/shops` if already authenticated

### 4.8 TypeScript Types

**File**: `src/types/index.ts`

Comprehensive type definitions for all entities:
- `User`, `Shop`, `Product`, `CartItem`, `Cart`, `Order`, `OrderItem`
- `ColdStorage`, `ColdStorageProduct`, `B2BOrder`, `B2BOrderItem`
- `Notification`, `ShopSchedule`, `CutType`
- Payload types: `B2BOrderPayload`, `SetPricePayload`, `ProductFormData`

### 4.9 WebSocket Integration

**File**: `src/lib/ws.ts`

WebSocket client for real-time updates:
- Connects to `/ws/orders/`
- Reconnects on disconnect
- Triggers data refetch on order events

---

## 5. Database Schema

### 5.1 Entity Relationship Diagram (Simplified)

```
User ──1:N──> Shop ──1:N──> Product ──1:N──> CutType
 │                      │
 │                      └──1:N──> ShopSchedule
 │                      └──1:N──> B2BOrder ──1:N──> B2BOrderItem
 │                      │                           │
 │                      │                           └──N:1──> ColdStorageProduct
 │                      └──1:N──> Order ──1:N──> OrderItem
 │
 └──1:1──> ColdStorage ──1:N──> ColdStorageProduct
 │
 └──1:N──> StaffActionLog
 │
 └──1:N──> B2BOrder (created_by)

Cart ──1:1──> User
CartItem ──N:1──> Cart
CartItem ──N:1──> Product
CartItem ──N:1──> CutType

LedgerEntry ──N:1──> Shop
LedgerEntry ──N:1──> ColdStorage
LedgerEntry ──N:1──> B2BOrder (optional)
LedgerEntry ──N:1──> User (collected_by)
LedgerEntry ──N:1──> User (weighted_by)

B2BOrderStatusHistory ──N:1──> B2BOrder
```

### 5.2 Key Database Constraints

| Model | Constraint | Purpose |
|-------|-----------|---------|
| Shop | `slug` unique | URL-safe unique identifier |
| ShopSchedule | `unique_together: [shop, weekday]` | One schedule per day per shop |
| Product | `unique_together: [shop, slug]` | Same product name allowed across shops |
| CartItem | `unique_together: [cart, product, cut_type]` | One entry per product+cut per cart |
| User | `phone` unique | Phone-based authentication |
| User | `email` unique (nullable) | Optional email with uniqueness |

---

## 6. API Endpoints Summary

### 6.1 Authentication
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login with phone + password |
| GET | `/api/auth/me/` | Get current user |
| PATCH | `/api/auth/me/` | Update current user |

### 6.2 Shops
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/shops/` | List verified shops (filter by city) |
| GET | `/api/shops/<slug>/` | Get shop detail |
| GET | `/api/shops/my-shop/` | Get authenticated user's shop |
| PATCH | `/api/shops/onboarding/` | Update shop details (resets verification) |
| GET/POST | `/api/shops/schedule/` | Get/set shop weekly schedule |
| PATCH | `/api/shops/<slug>/update/` | Update shop (owner only) |
| POST | `/api/shops/create-walkin/` | Create walk-in shop |
| POST | `/api/shops/become-shop-owner/` | Request shop owner role |
| POST | `/api/shops/cancel-owner-request/` | Cancel shop owner request |

### 6.3 Products
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/products/` | List products (filter by shop) |
| POST | `/api/products/` | Create product (shop owner) |
| PATCH | `/api/products/<id>/` | Update product |
| DELETE | `/api/products/<id>/` | Delete product |

### 6.4 Cart
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/cart/` | Get current user's cart |
| POST | `/api/cart/items/` | Add item to cart |
| PATCH | `/api/cart/items/<id>/` | Update cart item |
| DELETE | `/api/cart/items/<id>/` | Remove cart item |
| DELETE | `/api/cart/clear/` | Clear entire cart |

### 6.5 Orders (B2C)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/orders/checkout/` | Place order from cart |
| GET | `/api/orders/` | List user's orders |
| GET | `/api/orders/<id>/` | Get order detail |
| PATCH | `/api/orders/<id>/status/` | Update order status |

### 6.6 B2B (Cold Storage)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/b2b/cold-storages/` | List cold storages (shop owners) |
| GET | `/api/b2b/my-cold-storage/` | Get own cold storage |
| GET/POST | `/api/b2b/my-cold-storage/products/` | Manage products |
| POST | `/api/b2b/orders/` | Place B2B order |
| GET | `/api/b2b/orders/my-shop/` | Shop's B2B orders |
| GET | `/api/b2b/orders/incoming/` | Cold storage incoming orders |
| PATCH | `/api/b2b/orders/<id>/status/` | Update B2B order status |
| POST | `/api/b2b/orders/<id>/set-price/` | Set weight + price for piece items |
| PATCH | `/api/b2b/orders/<id>/confirm/` | Shop confirms priced order |
| GET | `/api/b2b/reports/daily/` | Daily sales report |
| GET/POST | `/api/b2b/ledger/` | Ledger entries |
| POST | `/api/b2b/ledger/payment/` | Record payment |
| GET | `/api/b2b/ledger/summary/` | Shop ledger summary |
| GET | `/api/b2b/ledger/balance/` | Shop balance |
| GET | `/api/map/locations/` | Role-based map locations |

### 6.7 Notifications
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/notifications/` | List notifications |
| PATCH | `/api/notifications/` | Mark all read |
| PATCH | `/api/notifications/<id>/` | Mark one read |
| DELETE | `/api/notifications/<id>/` | Delete notification |

---

## 7. Authentication & Authorization

### 7.1 Authentication Flow

```
1. User registers with phone + password (+ optional email, role)
2. Backend creates User + returns JWT (access: 1 day, refresh: 30 days)
3. Frontend stores tokens in cookies (access_token, refresh_token)
4. Every API request includes: Authorization: Bearer <access_token>
5. On 401, frontend clears cookies and redirects to /login
```

### 7.2 Role-Based Access Control

Permissions are enforced at multiple levels:

1. **Django Permissions** (`apps/common/permissions.py`):
   - `IsShopOwner`, `IsColdStorage`, `IsColdStorageOrStaff`, `IsShopOwnerOrColdStorage`
   - Custom `StaffPermission` checks individual permission flags

2. **Frontend Route Protection** (`middleware.ts`):
   - Protected routes require authentication
   - Auth routes redirect if already logged in

3. **Frontend Conditional Rendering**:
   - Navbar shows different links based on `user.role`
   - Dashboard pages check role and redirect if unauthorized

### 7.3 Staff Permission Model

Cold storage owners can create staff accounts with granular permissions:

| Permission | What it allows |
|-----------|---------------|
| `can_collect_payment` | Record payments in ledger |
| `can_view_ledger` | View ledger entries |
| `can_create_order` | Create walk-in orders |
| `can_manage_products` | CRUD on cold storage products |
| `can_view_orders` | View incoming B2B orders |
| `can_deliver_orders` | Update delivery status (processing → dispatched → delivered) |
| `can_confirm_orders` | Confirm B2B orders |

---

## 8. Key Business Flows

### 8.1 Customer Order Flow (B2C)

```
Customer browses shops → Selects shop → Views products
    → Adds to cart (with cut type) → Checkout
    → Chooses delivery or pickup
    → If pickup: chooses ASAP or scheduled time
    → Places order (COD) → Shop receives order
    → Shop updates status: pending → confirmed → preparing → out_for_delivery → delivered
    → Customer tracks order status
```

### 8.2 Shop Onboarding Flow

```
User registers as shop_owner → Fills shop details (name, phone, address, city)
    → Submits for verification → Admin reviews
    → Admin verifies → Shop appears in public listing
    → Shop owner adds products → Ready to receive orders
```

### 8.3 B2B Wholesale Order Flow

```
Shop owner browses cold storages → Selects cold storage
    → Views products (kg or piece based)
    → Adds items to order → Chooses delivery or pickup
    → Chooses payment: cash or credit
    → Places order

For KG-based items:
    → Order status: pending → confirmed → processing → dispatched → delivered
    → Price calculated immediately (quantity × price_per_kg)

For PIECE-based items:
    → Order status: pending_price (waiting for weighing)
    → Cold storage weighs each piece → Sets actual_weight_kg + price_per_kg_final
    → Order status: priced → Shop reviews and confirms → confirmed → processing → dispatched → delivered
    → Ledger entry created after pricing
```

### 8.4 Credit/Ledger Flow

```
B2B order placed with "credit" payment type
    → LedgerEntry created (type: credit, amount: order total)
    → Balance recalculated: total_credits - total_payments
    → Cold storage collects payment → LedgerEntry created (type: payment)
    → Balance decreases
    → If balance > ₹50,000 → credit limit exceeded warning
```

### 8.5 Walk-in Order Flow

```
Cold storage staff creates walk-in order:
    → Creates temporary shop (auto-verified, is_walkin=true)
    → Creates B2B order with source="walkin", payment_type="cash", delivery_type="pickup"
    → Order auto-pays (paid_amount = total_price)
    → Normal order processing follows
```

---

## 9. Deployment

### 9.1 Frontend (Vercel)

- Deployed at: `https://freshbaazaar.vercel.app`
- Environment variables:
  - `NEXT_PUBLIC_API_URL` — Backend API URL
- Automatic deployments on push to main branch

### 9.2 Backend (Render)

- Deployed at: `https://feshbazaar-api.onrender.com`
- PostgreSQL database (Render managed)
- `DATABASE_URL` from Render
- `DEBUG=False` in production
- WhiteNoise for static file serving
- Procfile: `web: gunicorn config.wsgi`

### 9.3 Environment Configuration

**Backend** (`Backend/.env`):
```
SECRET_KEY=<django-secret-key>
DEBUG=True
DB_NAME=freshbazaar_db
DB_USER=freshbazaar_user
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
```

**Frontend** (`FrontEnd/freshbazaar/.env.local`):
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

---

## 10. Development Setup

### 10.1 Backend

```bash
cd Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

### 10.2 Frontend

```bash
cd FrontEnd/freshbazaar
npm install
cp .env.example .env.local
npm run dev
```

### 10.3 Dependencies

**Backend** (key packages):
- Django 5.x
- djangorestframework
- djangorestframework-simplejwt
- django-cors-headers
- psycopg2 (PostgreSQL adapter)
- Pillow (image processing)
- channels (WebSocket)
- python-decouple (env management)
- whitenoise (static files)
- gunicorn (production WSGI)

**Frontend** (key packages):
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Zustand (state management)
- Axios (HTTP client)
- js-cookie (cookie management)
- framer-motion (animations)
- react-select (dropdowns)

---

## 11. Future Roadmap

### 11.1 Immediate Priorities

| Feature | Description | Priority |
|---------|-------------|----------|
| Payment Integration | Khalti / eSewa / Stripe | High |
| Delivery Tracking | Real-time rider location | High |
| Admin Dashboard | Shop verification, analytics | High |
| Reviews & Ratings | Customer feedback system | Medium |
| Nepali Language | Full i18n support (नेपाली) | Medium |

### 11.2 Medium-term

| Feature | Description |
|---------|-------------|
| AI Demand Prediction | Predict order volumes for shops |
| Festival Booking | Special orders for Dashain, Tihar, Eid |
| Freshness Tracking | Batch tracking, expiry dates |
| Multi-city Expansion | City-based shop discovery |
| SMS Notifications | Order updates via SMS |
| Dark Mode | Full dark theme support |

### 11.3 Long-term

| Feature | Description |
|---------|-------------|
| Mobile App | React Native iOS/Android |
| Live Price Board | Real-time meat market prices |
| Subscription Plans | Premium shop features |
| Commission System | Platform revenue automation |
| Farm Traceability | Source tracking for meat |
| Analytics Dashboard | Advanced business intelligence |

---

## Appendix A: Order Status Flowcharts

### B2C Order Status
```
pending → confirmed → preparing → out_for_delivery → delivered
   ↓          ↓           ↓                              ↓
cancelled   cancelled   cancelled                     (complete)
```

### B2B Order Status
```
pending_price → priced → confirmed → processing → dispatched → delivered
     ↓             ↓         ↓
  cancelled    cancelled  cancelled
```

## Appendix B: Key File Locations

| Purpose | Backend File | Frontend File |
|---------|-------------|---------------|
| User model | `apps/accounts/models.py` | `src/types/index.ts` |
| Shop model | `apps/shops/models.py` | `src/types/index.ts` |
| Product model | `apps/products/models.py` | `src/types/index.ts` |
| B2B models | `apps/b2b/models.py` | `src/types/index.ts` |
| Permissions | `apps/common/permissions.py` | `src/middleware.ts` |
| Main settings | `config/settings.py` | `next.config.ts` |
| URL routing | `config/urls.py` | `src/app/` (file-based) |
| API client | — | `src/lib/api.ts` |
| Auth store | — | `src/store/authStore.ts` |
| Navbar | — | `src/components/layout/Navbar.tsx` |

## Appendix C: Time Zone & Localization

- **Time Zone**: `Asia/Kathmandu` (Nepal Standard Time, UTC+5:45)
- **Currency**: NPR (₨ / Rs.)
- **Language**: English (Nepali planned)
- **Date Format**: English numerals, locale-appropriate formatting

## Appendix D: Security Considerations

1. **JWT tokens** stored in HTTP cookies (not localStorage)
2. **CORS** configured for specific origins in production
3. **CSRF** protection enabled
4. **Password hashing** via Django's built-in PBKDF2
5. **Phone-based auth** — more reliable in Nepal than email
6. **Role-based access** — enforced at API and frontend levels
7. **Media files** — served via WhiteNoise in production (consider S3/Cloudflare R2 for scale)

---

*Document generated from codebase analysis. Last updated: April 2026*
*Author: Sudhir Tamang*
*Project: FreshBazaar — Fresh Meat Delivery Platform*
