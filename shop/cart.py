from decimal import Decimal
from .models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.data = self.session.get('cart', {})

    def save(self):
        self.session['cart'] = self.data
        self.session.modified = True

    def set(self, product, quantity):
        if quantity <= 0:
            self.data.pop(str(product.pk), None)
        else:
            self.data[str(product.pk)] = min(quantity, 99)
        self.save()

    def add(self, product):
        self.set(product, self.data.get(str(product.pk), 0) + 1)

    def items(self):
        products = Product.objects.filter(pk__in=self.data, available=True)
        result = []
        active = set()
        for product in products:
            key = str(product.pk)
            active.add(key)
            quantity = self.data[key]
            result.append({'product': product, 'quantity': quantity, 'total': product.price * quantity})
        stale = set(self.data) - active
        if stale:
            for key in stale:
                self.data.pop(key)
            self.save()
        return result

    def total(self):
        return sum((item['total'] for item in self.items()), Decimal('0'))
