
from .models import *

def header_context(request):
    # ১. Wishlist Count
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

    # ২. Compare Count
    compare_count = len(request.session.get('compare_list', []))

    # ৩. Cart Count & Total Price
    cart = request.session.get('cart', {})
    cart_count = 0
    total_price = 0

    if isinstance(cart, dict):
        for product_id, item_data in cart.items():
            if isinstance(item_data, dict):
                quantity = item_data.get('quantity', 1)
            else:
                try:
                    quantity = int(item_data)
                except (ValueError, TypeError):
                    quantity = 1

            cart_count += quantity

            try:
                product = Product.objects.get(id=product_id)
                total_price += product.price * quantity
            except Product.DoesNotExist:
                continue

    return {
        'wishlist_count': wishlist_count,
        'compare_count': compare_count,
        'cart_count': cart_count,
        'total_price': total_price,
    }



def categories_processor(request):
    return {
        'categories': Category.objects.all()
    }