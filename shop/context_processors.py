from .cart import Cart

def cart_summary(request):
    return {'cart_count': sum(item['quantity'] for item in Cart(request).items())}
