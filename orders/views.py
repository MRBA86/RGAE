from datetime import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .cart import Cart
from products.models import Product
from .forms import CartAddForm, OrderAddressForm, CouponAplyForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order, OrderItem, Coupon
from django.contrib import messages
from accounts.models import Address
import jdatetime
#from django_jalali.

class CartView(View):
    
    def get(self, request):
        cart = Cart(request)
        return render(request, 'orders/cart.html', {'cart': cart})
    
class CartAddView(View):
    
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id= product_id)
        form = CartAddForm(request.POST)
        if form.is_valid():
            cart.add(product, form.cleaned_data['quantity'])
        return redirect('orders:cart')
    
class CartRemoveView(View):
    
    def get(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect('orders:cart')


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        order = Order.objects.create(user=request.user, status=Order.Status.PENDING_PAYMENT)
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'], price= item['price'], quantity=item['quantity'])
            
        cart.clear()
        messages.success(request, 'سفارش ایجاد شد.', 'success')
        return redirect('orders:order_detail', order.id)
    
    
class OrderDetailView(LoginRequiredMixin, View):
    form_class = CouponAplyForm
    def get(self, request, order_id):
        form = self.form_class
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'orders/checkout.html', {'order':order, 'form': form})
    
class CouponApplyView(LoginRequiredMixin, View):
    form_class = CouponAplyForm
    
    def post(self, request, order_id):
        form = self.form_class(request.POST)
        now = jdatetime.datetime.now()
        if form.is_valid():
            code = form.cleaned_data['code']
            print(code)
            print(now)
            try:
                coupon = Coupon.objects.get(code__exact=code, valid_from__lte=now, valid_to__gte=now, active=True)
            except Coupon.DoesNotExist:
                messages.error(request, 'کد تخفیف وارده معتبر نمی باشد', 'danger')
                return redirect('orders:order_detail', order_id)
            order = Order.objects.get(id=order_id)
            order.discount = coupon.discount
            order.save()
            return redirect('orders:order_detail', order_id)
                            


# orders/views.py
class AddAddressToOrderView(LoginRequiredMixin, View):
    """افزودن آدرس به سفارش موجود"""
    form_class = OrderAddressForm
    template_name = 'orders/add_address.html'
    
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user, status=Order.Status.PENDING_ADDRESS)
        
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form, 'order': order})
    
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user, status=Order.Status.PENDING_ADDRESS) 
        form = self.form_class(request.user, request.POST)
        
        if form.is_valid():
            address_choice = form.cleaned_data['address_choice']
            
            if address_choice == self.form_class.USE_EXISTING_ADDRESS:
                # استفاده از آدرس موجود
                existing_address = form.cleaned_data['existing_address']
                order.shipping_address = existing_address
                
            elif address_choice == self.form_class.USE_NEW_ADDRESS:
                # ایجاد آدرس جدید
                new_address = Address(
                    user=request.user,
                    title=form.cleaned_data.get('new_title', 'آدرس جدید'),
                    province=form.cleaned_data['new_province'],
                    city=form.cleaned_data['new_city'],
                    postal_code=form.cleaned_data['new_postal_code'],
                    address=form.cleaned_data['new_address'],
                    plaque=form.cleaned_data['new_plaque'],
                    unit=form.cleaned_data.get('new_unit', ''),
                    receiver_first_name=form.cleaned_data['new_receiver_first_name'],
                    receiver_last_name=form.cleaned_data['new_receiver_last_name'],
                    receiver_phone=form.cleaned_data['new_receiver_phone'],
                )
                
                # ذخیره آدرس جدید
                if form.cleaned_data.get('save_new_address'):
                    new_address.save()
                    if not Address.objects.filter(user=request.user, is_default=True).exists():
                        new_address.is_default = True
                        new_address.save()
                    order.shipping_address = new_address
            
            # تغییر وضعیت سفارش
            order.status = Order.Status.PENDING_PAYMENT
            order.address_submitted_at = timezone.now()
            order.save()
            
            messages.success(request, 'آدرس با موفقیت ثبت شد', 'success')
            return redirect('orders:payment', order_id=order.id)        
        return render(request, self.template_name, {'form': form, 'order': order})

# orders/views.py
class PaymentView(LoginRequiredMixin, View):
    """پرداخت سفارش"""
    
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user, status=Order.Status.PENDING_PAYMENT)
        
        # بررسی اینکه سفارش آدرس دارد
        if not order.order_address :
            messages.error(request, 'لطفاً ابتدا آدرس تحویل را وارد کنید', 'warning')
            return redirect('orders:add_address', order_id=order.id)    
        return render(request, 'orders/payment.html', {'order': order})
    
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user, status=Order.Status.PENDING_PAYMENT)
        
        # در اینجا کد پرداخت واقعی (زرین‌پال، بانک، ...)
        # فرض می‌کنیم پرداخت موفق بود
        
        # تغییر وضعیت سفارش
        order.status = Order.Status.PAID
        order.paid = True
        order.paid_at = timezone.now()
        order.save(using= self._db)

        messages.success(request, 'پرداخت با موفقیت انجام شد. سفارش شما ثبت شد.', 'success')
        return redirect('orders:order_detail', order_id=order.id)
    
    
