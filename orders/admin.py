from django.contrib import admin
from orders.models import Order, OrderItem, Coupon

@admin.action(description="تایید سفارشات اقساطی")
def approve_installment_orders(modeladmin, request, queryset):
    queryset.update(status=Order.Status.PENDING)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_number', 'user', 'payment_type', 'status', 'updated_at')
    list_filter = ('paid',)
    inlines = (OrderItemInline,)
    actions = [approve_installment_orders]
    
admin.site.register(Coupon)