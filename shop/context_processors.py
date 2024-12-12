from .cart import Cart

def cart(request):
    print("Cart context processor is being called")  # Debugging line
    return {'cart': Cart(request)}