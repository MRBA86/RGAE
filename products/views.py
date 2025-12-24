from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Product, ProductImage
from orders.forms import CartAddForm


class ProductsView(View):
    def get(self, request):
        
        products = Product.objects.filter(available=True)
        return render(request, 'products/products.html', {'products': products})
        
    
class ProductDetailView(View):
    
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug, available=True )
        form = CartAddForm()
        images = product.all_images
        primary_image = product.primary_image
        return render(request, 'products/product_detail.html', {'product': product , 'form': form, 'primary_image': primary_image, 'images':images})

    
# Create your views here.
