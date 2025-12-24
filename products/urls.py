from django.urls import path, re_path
from .views import ProductsView, ProductDetailView

app_name = 'products'

urlpatterns = [
    path('', ProductsView.as_view(), name='products'),
    re_path(r'(?P<slug>[-\w\u0600-\u06FF]+)/$', ProductDetailView.as_view(), name='product_detail'),
]
