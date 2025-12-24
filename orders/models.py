from django.db import models
from accounts.models import User, Address
from products.models import Product
import django_jalali.db.models as jmodels


class Order(models.Model):
    
    class Status(models.TextChoices):
        PENDING_ADDRESS = 'pending_address', 'در انتظار آدرس'
        PENDING_PAYMENT = 'pending_payment', 'در انتظار پرداخت'
        PAID = 'paid', 'پرداخت شده'
        PROCESSING = 'processing', 'در حال پردازش'
        COMPLETED = 'completed', 'تکمیل شده'
        CANCELLED = 'cancelled', 'لغو شده'
        
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_orders', verbose_name = "کاربر")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_ADDRESS ) # وضعیت پیش‌فرض
    order_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    paid = models.BooleanField(verbose_name = "پرداخت شده ؟", default=False)
    created_at = jmodels.jDateTimeField(verbose_name = "تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField(verbose_name = "تاریخ ویرایش", auto_now=True)
    address_submitted_at = jmodels.jDateTimeField(verbose_name="تاریخ ثبت آدرس", null=True, blank=True)
    paid_at = jmodels.jDateTimeField(verbose_name="تاریخ پرداخت سفارش", null=True, blank=True)
    
    @property
    def order_number(self):
        return f'RGAE{self.created_at.year}-{self.id}'

    class Meta:
        ordering = ('paid', '-updated_at')
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش ها'
        
    def __str__(self):
        return f'{self.order_number}'
    
    
    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())
    
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete= models.CASCADE, related_name='items', verbose_name = "سفارش")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name = "محصول")
    price = models.IntegerField(verbose_name = "قیمت")
    quantity = models.IntegerField(verbose_name = "تعداد", default=1)
    
    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم های سفارش'
    
    def __str__(self):
        return str(self.id)
        
    
    def get_cost(self):
        return self.price * self.quantity

