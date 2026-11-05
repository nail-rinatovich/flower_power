from django.core.management.base import BaseCommand
from shop.models import Category, Product


class Command(BaseCommand):
    help = 'Добавляет демонстрационные букеты, не изменяя существующие товары.'

    def handle(self, *args, **options):
        categories = {slug: Category.objects.get_or_create(slug=slug, defaults={'name': name})[0]
                      for slug, name in [('bouquets', 'Авторские букеты'), ('roses', 'Розы'), ('mono', 'Монобукеты'), ('boxes', 'Цветы в коробке')]}
        data = [
            ('pink-cloud', 'Розовое облако', 'bouquets', 4290, 'Хит', 'photo-1563241527-3004b7be0ffd', 'Пионовидные розы, эустома, эвкалипт'),
            ('morning', 'Доброе утро', 'mono', 2790, 'Новинка', 'photo-1520763185298-1b434c919102', 'Сезонные тюльпаны, 25 шт.'),
            ('love-letter', 'Письмо о любви', 'roses', 5490, '', 'photo-1518895949257-7621c3c786d7', 'Розовые розы, 21 шт., зелень'),
            ('wild-garden', 'Дикий сад', 'bouquets', 3890, 'Выбор флориста', 'photo-1457089328109-e5d9bd499191', 'Сезонные цветы, кустовые розы, зелень'),
            ('soft-touch', 'Нежное прикосновение', 'boxes', 4790, '', 'photo-1561181286-d3fee7d55364', 'Розы, гортензия, эустома, шляпная коробка'),
            ('summer', 'Маленькое лето', 'mono', 2490, '', 'photo-1490750967868-88aa4486c946', 'Сезонные цветы в воздушной упаковке'),
            ('white-story', 'Белая история', 'roses', 4990, '', 'photo-1525310072745-f49212b5ac6d', 'Белые розы, 25 шт.'),
            ('for-you', 'Только для тебя', 'bouquets', 5990, 'Особенный', 'photo-1531058020387-3be344556be6', 'Авторский микс из сезонных цветов'),
        ]
        for slug, name, category, price, badge, photo, composition in reversed(data):
            Product.objects.get_or_create(slug=slug, defaults={
                'name': name, 'category': categories[category], 'price': price, 'badge': badge,
                'image_url': f'https://images.unsplash.com/{photo}?auto=format&fit=crop&w=1000&q=85',
                'description': 'Букет для тёплых слов и маленьких знаков внимания. Нежные оттенки, живые фактуры и бережная сборка вручную. Каждый букет немного отличается — в этом и есть красота живых цветов.',
                'composition': composition,
            })
        self.stdout.write(self.style.SUCCESS('Демонстрационный каталог готов.'))
