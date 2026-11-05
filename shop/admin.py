from django.contrib import admin
from .models import Category, Product

admin.site.site_header = 'Flower Power · управление магазином'
admin.site.site_title = 'Flower Power'
admin.site.index_title = 'Ваш цветочный магазин'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'available', 'badge']
    list_filter = ['category', 'available']
    list_editable = ['price', 'available']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
