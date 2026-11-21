from django.contrib import admin
from django.urls import include, path
from .views import health, product_image

urlpatterns = [
    path('healthz/', health, name='health'),
    path('media/<path:filename>', product_image, name='product_image'),
    path('admin/', admin.site.urls), path('', include('shop.urls')),
]
