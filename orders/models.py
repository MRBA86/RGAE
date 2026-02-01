from django.db import models
from accounts.models import User, Address
from products.models import Product
import django_jalali.db.models as jmodels
from django.core.validators import MinValueValidator, MaxValueValidator


class Order(models.Model):
    
    class PaymentType(models.TextChoices):
        CASH = 'cash', 'پرداخت نقدی'
        INSTALLMENT = 'installment', 'پرداخت اقساطی (اسنپ‌پی)'

    
    class Status(models.TextChoices):
        WAITING_FOR_ADDRESS = 'waiting_address', 'در انتظار ثبت آدرس'
        WAITING_FOR_PAYMENT = 'waiting_payment', 'در انتظار انتخاب روش پرداخت'
        WAITING_APPROVAL = 'waiting_approval', 'در انتظار تأیید مدیر'
        PENDING = 'pending', 'در انتظار پرداخت'        
        PAID = 'paid', 'پرداخت شده'
        CANCELED = 'canceled', 'لغو شده'
        
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_orders', verbose_name = "کاربر")
    payment_type = models.CharField(max_length=20, choices=PaymentType.choices, null=True, blank=True, verbose_name = "نوع پرداخت")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING_FOR_ADDRESS, verbose_name = "وضعیت سفارش" ) # وضعیت پیش‌فرض
    order_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    paid = models.BooleanField(verbose_name = "پرداخت شده ؟", default=False)
    created_at = jmodels.jDateTimeField(verbose_name = "تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField(verbose_name = "تاریخ ویرایش", auto_now=True)
    address_submitted_at = jmodels.jDateTimeField(verbose_name="تاریخ ثبت آدرس", null=True, blank=True)
    paid_at = jmodels.jDateTimeField(verbose_name="تاریخ پرداخت سفارش", null=True, blank=True)
    discount = models.IntegerField(verbose_name="تخفیف سفارش",blank=True, null=True, default=None)
    
    @property
    def order_number(self):
        return f'RGAE{self.created_at.year}-{self.id}'
    
    @property
    def discount_price(self):
        if self.discount:
            return int((self.discount / 100) * self.get_total_price())
        return None
    
    class Meta:
        ordering = ('paid', '-updated_at')
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش ها'
        
    def __str__(self):
        return f'{self.order_number}'
    
    
    def get_total_price(self):
        total = sum(item.get_cost() for item in self.items.all())
        if self.discount:
            discount_price = (self.discount / 100) * total
            return int(total - discount_price)
        return total
    
    
    
    
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

class Coupon(models.Model):
    code = models.CharField(verbose_name="کد تخفیف", max_length=30)
    valid_from = jmodels.jDateTimeField(verbose_name="تاریخ شروع اعتبار")
    valid_to = jmodels.jDateTimeField(verbose_name="تاریخ پایان اعتبار")
    discount = models.IntegerField(verbose_name="درصد تخفیف", validators=[MinValueValidator(0), MaxValueValidator(90)])
    active = models.BooleanField(verbose_name="فعال بودن کد", default=False)
    
    class Meta:
        verbose_name = 'کد تخفیف'
        verbose_name_plural = 'کدهای تخفیف'
    
    
    
    def __str__(self):
        return self.code
    

    
    