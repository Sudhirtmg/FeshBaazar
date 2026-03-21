1️⃣ Project Vision

Goal

Build a system where:

Customers → order meat
Meat shops → manage orders
Cold stores → supply shops
Platform → manages the ecosystem

First test with your mom’s shop, then expand to many shops.

2️⃣ Platform Flow

Basic flow:

Customer
   ↓
Order Meat (website/app)
   ↓
Shop Dashboard
   ↓
Shop prepares order
   ↓
Customer pickup

Later:

Cold Store
   ↓
Supply Meat to Shops
3️⃣ System Architecture

Frontend + Backend structure:

MEAT_SHOP/

 ├ Backend/
 │   ├ Django API
 │   ├ PostgreSQL database
 │   └ Business logic
 │
 └ FrontEnd/
     ├ Next.js
     └ User interface

Communication:

Next.js → API → Django → Database
4️⃣ Backend Apps (Django)

Your backend should eventually contain these apps:

shops
customers
orders
inventory
suppliers
payments
analytics

Explanation:

App	Purpose
shops	Meat shop profiles
customers	customer information
orders	meat orders
inventory	daily stock tracking
suppliers	cold store suppliers
payments	eSewa/Khalti payments
analytics	sales insights
5️⃣ Core Database Models

Important tables:

Shop
Shop
- id
- name
- owner_name
- phone
- address
- created_at
Customer
Customer
- id
- name
- phone
Order
Order
- id
- shop
- customer
- quantity
- pickup_time
- status
- created_at

Status system:

pending
arrived
cutting
completed
cancelled
Inventory
Inventory
- shop
- date
- starting_stock
- sold
- remaining
6️⃣ Order Flow

The workflow should look like this:

Customer places order
        ↓
Order appears in shop dashboard
        ↓
Customer arrives
        ↓
Shop cuts meat
        ↓
Order completed
7️⃣ Frontend Pages

Customer side:

Home
Shop page
Order page
Order confirmation

Shop dashboard:

Login
Today's orders
Order status
Sales report
Inventory
8️⃣ MVP Features (First Version)

Version 1 should only include:

Customer order page
Shop dashboard
Order status system
Daily stock tracking
Sales report

Nothing more.

9️⃣ Future Features

Later you can add:

Delivery system
Cold store supply system
AI demand prediction
Shop ratings
Multiple shop marketplace
Online payments
🔟 Business Model

Later revenue sources:

Shop subscription
Order commission
Supplier listing
Delivery service fee
11️⃣ Development Roadmap

Step-by-step build plan:

1 Build backend structure
2 Create shop model
3 Create customer model
4 Create order system
5 Build shop dashboard
6 Build customer order page
7 Test in mom's shop
8 Improve system
9 Add multi-shop support
10 Expand platform
⭐ Very Important

Whenever you come back to the project, you can simply tell an AI:

This is my meat shop platform architecture.

Backend: Django + DRF
Frontend: Next.js

Current progress: Django project created.

Next task: build the shop model.

Then AI can continue development immediately.


------------------------------------------------------------------------------------------
1. Main Idea of the Backend

Your backend should manage 5 core things:

Users

Shops

Products

Orders

Delivery

That is your MVP.

Later you can add:

payments

subscriptions

analytics

cold storage

butcher booking

live price board

So first let’s design the core properly.

2. Recommended Django Apps Structure

Since you asked before about clean structure, yes — splitting things into separate apps is a good idea.

Example:

backend/
├── accounts/
├── shops/
├── products/
├── cart/
├── orders/
├── deliveries/
├── payments/
├── reviews/
├── notifications/
└── common/
What each app does

accounts

customer

shop owner

admin

delivery rider

shops

shop profile

shop address

opening hours

shop verification

products

meat items

categories

stock

cut types

pricing

cart

user cart

cart items

orders

placed orders

order items

status history

deliveries

delivery assignment

rider tracking

delivery status

payments

COD

online payment records

reviews

shop review

product review

notifications

SMS/email/push logs

common

reusable helpers

base models

utilities

3. User Roles You Should Support

You should not keep only one type of user.

Use one custom user model and give roles.

Example roles

customer

shop_owner

staff

delivery_rider

admin

Example
class User(AbstractUser):
    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("shop_owner", "Shop Owner"),
        ("delivery_rider", "Delivery Rider"),
        ("admin", "Admin"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")
    phone = models.CharField(max_length=20, unique=True)

This helps a lot later.

4. Shop Model Design

A shop is very important because in your model, many products belong to a shop.

Shop should contain:

owner

shop name

slug

description

phone

address

city

latitude/longitude

open/closed status

verified status

Example
class Shop(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shops")
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_open = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
5. Product Model Design

This is where your meat items live.

Each product belongs to a shop.

Product should contain:

shop

category

name

description

price

discounted price

stock quantity

unit

image

availability

freshness info later

Example
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

class Product(models.Model):
    UNIT_CHOICES = (
        ("kg", "Kilogram"),
        ("piece", "Piece"),
        ("pack", "Pack"),
    )

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default="kg")
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("shop", "slug")
6. Cut Type Model — Very Useful for Meat

This is special for your business.

Not all products have the same cut options.

Example:

Chicken can have:

curry cut

boneless

bbq cut

small pieces

Goat can have:

normal cut

small curry cut

sekuwa cut

So create a separate model.

class CutType(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cut_types")
    name = models.CharField(max_length=100)
    extra_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

This is a very smart business feature.

7. Cart Model

Keep cart separate from orders.

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cut_type = models.ForeignKey(CutType, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

Why store price_at_time?
Because product price may change later.

8. Order Model Design

This is the heart of the system.

Order should store:

customer

shop

delivery address

total price

payment method

order status

class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("preparing", "Preparing"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    PAYMENT_METHODS = (
        ("cod", "Cash on Delivery"),
        ("online", "Online Payment"),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="cod")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_name = models.CharField(max_length=255)
    delivery_phone = models.CharField(max_length=20)
    delivery_address = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
Order Items
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)
    cut_type_name = models.CharField(max_length=100, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

Store product_name and cut_type_name too, because later product names may change.

9. Delivery Model

You may not need advanced rider tracking on day one, but keep a simple delivery table.

class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="delivery")
    rider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="deliveries")
    assigned_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, default="pending")
10. Review Model

Trust is everything for meat business.

class ShopReview(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

Later you can add:

hygiene rating

freshness rating

packaging rating

That will make FreshBazaar stronger.

11. Inventory Design

For now, stock_quantity in Product is enough.

Later, if business grows, create:

StockEntry

StockAdjustment

StockLog

Example later:

added 20 kg chicken

sold 5 kg

wasted 1 kg

But for MVP, don’t overcomplicate.

12. APIs You Should Build First

Now let’s talk about the actual endpoints.

Auth

POST /api/auth/register/

POST /api/auth/login/

GET /api/auth/me/

Shops

GET /api/shops/

GET /api/shops/<slug>/

POST /api/shops/ for owner/admin

Products

GET /api/products/

GET /api/products/<id>/

POST /api/products/

PATCH /api/products/<id>/

DELETE /api/products/<id>/

Cart

GET /api/cart/

POST /api/cart/items/

PATCH /api/cart/items/<id>/

DELETE /api/cart/items/<id>/

Orders

POST /api/orders/checkout/

GET /api/orders/

GET /api/orders/<id>/

PATCH /api/orders/<id>/status/

Reviews

POST /api/reviews/shops/

GET /api/shops/<slug>/reviews/

13. Best MVP Flow

Here is the flow I recommend for version 1:

Customer side

User registers

User views nearby shop

User views products

User selects meat + cut type

Adds to cart

Places order

Shop receives order

Shop changes status

Delivery completes

Shop owner side

Create shop profile

Add products

Update stock

Receive orders

Update order status

That’s enough for a first real version.

14. Folder Structure Inside Each App

Since you asked about separate serializers and views folders before — yes, that’s good architecture if you stay organized.

Example for products app:

products/
├── models.py
├── urls.py
├── serializers/
│   ├── __init__.py
│   ├── product_serializer.py
│   ├── category_serializer.py
│   └── cut_type_serializer.py
├── views/
│   ├── __init__.py
│   ├── product_views.py
│   ├── category_views.py
│   └── cut_type_views.py
├── services/
│   └── product_service.py
└── permissions.py

This is good when the project grows.

For a tiny project, it can feel heavy.
But for FreshBazaar, this structure is actually fine.

15. What Not to Build Yet

Don’t build these first:

AI demand prediction

live camera system

advanced rider tracking map

multi-warehouse system

farm traceability blockchain type things

real-time analytics dashboards everywhere

These are exciting, but they will delay launch badly.

16. Best Technical Stack for Your Case

For your current stage:

Backend

Django

Django REST Framework

PostgreSQL

JWT auth

Pillow for image upload

Later

Redis

Celery

Stripe/Khalti/eSewa integration

Docker

Nginx

S3/Bunny/Cloudflare R2 for media

17. The Smartest Launch Plan

Here’s the best business + technical path:

Phase 1

Single shop

your mom’s shop

products

cart

orders

COD

Phase 2

Multi-shop

multiple shop owners

separate dashboards

city filtering

Phase 3

Delivery layer

riders

assignment

basic tracking

Phase 4

Platform monetization

commission

featured shops

subscription plans

Phase 5

Advanced features

freshness tracking

live price board

festival booking

analytics

18. My Honest Recommendation for You Right Now

Build these models first:

User

Shop

Category

Product

CutType

Cart

CartItem

Order

OrderItem

That is the strongest starting point.

If you build these cleanly, the rest becomes much easier.

19. Very Important Business Advice

Since your idea is for Nepal meat shops, one of your biggest advantages is not just code.

It is this:

you understand the local real-life problem.

That matters more than fancy code.

If FreshBazaar makes ordering meat:

easier

cleaner

more trustworthy

then even a simple MVP can become valuable.