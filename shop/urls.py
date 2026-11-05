from django.urls import path
from . import views
app_name = 'shop'
urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('flowers/<slug:slug>/', views.product, name='product'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add'),
    path('cart/update/<int:pk>/', views.update_cart, name='update'),
]
