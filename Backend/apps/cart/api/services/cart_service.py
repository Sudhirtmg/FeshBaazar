from apps.cart.models import Cart, CartItem
from apps.products.models import Product

# If item exists → increase quantity
# If not → create new cart item

def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


def add_item_to_cart(user, product_id, quantity):

    cart = get_or_create_cart(user)

    product = Product.objects.get(id=product_id)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            "quantity": quantity,
            "price_at_time": product.price
        }
    )

    if not created:
        item.quantity += quantity
        item.save()

    return item