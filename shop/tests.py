from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from .models import Category, Product
from django.test import override_settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from tempfile import TemporaryDirectory


class ShopTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Розы', slug='roses')
        cls.product = Product.objects.create(name='Нежные розы', slug='roses', category=cls.category, price='4290.50', description='Букет роз')
        cls.hidden = Product.objects.create(name='Скрытый', slug='hidden', category=cls.category, price=100, available=False)

    def test_catalog_and_filters(self):
        response = self.client.get('/')
        self.assertContains(response, self.product.name)
        self.assertNotContains(response, self.hidden.name)
        self.assertContains(self.client.get('/?q=Нежные&category=roses&sort=price'), self.product.name)
        self.assertNotContains(self.client.get('/?q=тюльпан'), self.product.name)
        self.assertEqual(self.client.get(self.product.get_absolute_url()).status_code, 200)
        self.assertEqual(self.client.get(self.hidden.get_absolute_url()).status_code, 404)

    def test_cart_add_update_remove_and_session(self):
        url = reverse('shop:add', args=[self.product.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url)
        self.client.post(url)
        response = self.client.get(reverse('shop:cart'))
        self.assertEqual(response.context['total'], Decimal('8581.00'))
        self.assertEqual(response.context['cart_count'], 2)
        # Another browser session must have an independent cart.
        self.assertEqual(Client().get(reverse('shop:cart')).context['cart_count'], 0)
        self.client.post(reverse('shop:update', args=[self.product.pk]), {'quantity': 3})
        self.assertEqual(self.client.get(reverse('shop:cart')).context['total'], Decimal('12871.50'))
        self.client.post(reverse('shop:update', args=[self.product.pk]), {'quantity': 0})
        self.assertEqual(self.client.get(reverse('shop:cart')).context['total'], 0)

    def test_hidden_deleted_and_current_prices(self):
        self.client.post(reverse('shop:add', args=[self.product.pk]))
        self.product.price = 5000
        self.product.save()
        self.assertEqual(self.client.get(reverse('shop:cart')).context['total'], 5000)
        self.product.available = False
        self.product.save()
        self.assertEqual(self.client.get(reverse('shop:cart')).context['cart_count'], 0)
        self.assertEqual(self.client.post(reverse('shop:add', args=[self.hidden.pk])).status_code, 404)

    def test_quantity_validation(self):
        self.client.post(reverse('shop:add', args=[self.product.pk]))
        for quantity in ['bad', '-1', '100', '9' * 5000]:
            self.client.post(reverse('shop:update', args=[self.product.pk]), {'quantity': quantity})
            self.assertEqual(self.client.get(reverse('shop:cart')).context['cart_count'], 1)

    def test_post_requires_csrf(self):
        self.assertEqual(Client(enforce_csrf_checks=True).post(reverse('shop:add', args=[self.product.pk])).status_code, 403)

    def test_admin_can_add_product(self):
        admin = get_user_model().objects.create_superuser('florist', 'florist@example.com', 'Strong-Test-Password-2026')
        self.assertEqual(self.client.get('/admin/shop/product/add/').status_code, 302)
        self.client.force_login(admin)
        response = self.client.post('/admin/shop/product/add/', {
            'name': 'Новый букет', 'slug': 'new', 'category': self.category.pk,
            'description': 'Новый букет из админки', 'price': '2900.00', 'available': 'on', '_save': 'Сохранить',
        })
        self.assertEqual(response.status_code, 302)
        self.assertContains(self.client.get('/'), 'Новый букет')

    def test_demo_command_idempotent(self):
        from django.core.management import call_command
        call_command('seed_shop', verbosity=0)
        count = Product.objects.count()
        call_command('seed_shop', verbosity=0)
        self.assertEqual(Product.objects.count(), count)

    def test_uploaded_product_photo_in_production(self):
        # Uploads must remain accessible when Django's DEBUG-only serving is off.
        with TemporaryDirectory() as directory:
            with override_settings(MEDIA_ROOT=directory, DEBUG=False, SECURE_SSL_REDIRECT=False):
                self.product.image.save('flower.png', ContentFile(b'photo-content'), save=True)
                response = self.client.get(self.product.image.url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(b''.join(response.streaming_content), b'photo-content')
                response.close()
                orphan = default_storage.save('not-a-product.txt', ContentFile(b'private'))
                self.assertEqual(self.client.get('/media/' + orphan).status_code, 404)
                self.assertEqual(self.client.get('/media/missing.png').status_code, 404)

    def test_health_checks_database(self):
        from unittest.mock import patch
        from django.db import DatabaseError
        self.assertJSONEqual(self.client.get('/healthz/').content, {'status': 'ok'})
        with patch('flower_power.views.connection.cursor', side_effect=DatabaseError):
            response = self.client.get('/healthz/')
            self.assertEqual(response.status_code, 503)
            self.assertJSONEqual(response.content, {'status': 'unavailable'})
