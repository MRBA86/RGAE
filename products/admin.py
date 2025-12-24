from django.contrib import admin
from .models import Product, ProductImage, Category, Modem


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'price', 'category', 'available')
    inlines = [ProductImageInline]
    
    
@admin.register(Modem)
class ModemAdmin(admin.ModelAdmin):
    list_display = ('product', 'wifi_technology', 'pon')

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    
    
admin.site.register(Category, CategoryAdmin)