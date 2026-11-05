from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('Адрес', unique=True)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ['id']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('Название', max_length=180)
    slug = models.SlugField('Адрес', unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Категория', related_name='products')
    description = models.TextField('Описание')
    composition = models.CharField('Состав', max_length=300, blank=True)
    price = models.DecimalField('Цена, ₽', max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    image = models.ImageField('Фотография', upload_to='products/%Y/%m/', blank=True)
    image_url = models.URLField('Ссылка на фотографию', blank=True, help_text='Используется, если фотография не загружена.')
    badge = models.CharField('Метка', max_length=30, blank=True, help_text='Например: Хит или Новинка')
    available = models.BooleanField('В продаже', default=True)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
        constraints = [models.CheckConstraint(condition=models.Q(price__gte=1), name='product_price_positive')]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product', args=[self.slug])

    @property
    def photo(self):
        return self.image.url if self.image else self.image_url or '/static/shop/placeholder.svg'
