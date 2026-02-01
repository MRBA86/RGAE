from django.utils import timezone as tz
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .cart import Cart
from products.models import Product
from .forms import CartAddForm, OrderAddressForm, CouponApplyForm, PaymentMethodForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order, OrderItem, Coupon
from django.contrib import messages
from accounts.models import Address
import jdatetime
#from django_jalali.
from django.views.generic import TemplateView


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
        order = Order.objects.create(user=request.user, status=Order.Status.WAITING_FOR_ADDRESS)
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'], price= item['price'], quantity=item['quantity'])
            
        cart.clear()
        messages.success(request, 'سفارش ایجاد شد.', 'success')
        return redirect('orders:add_address', order.id)
    
    
class OrderDetailView(LoginRequiredMixin, View):
    form_class = CouponApplyForm
    def get(self, request, order_id):
        form = self.form_class
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'orders/checkout.html', {'order':order, 'form': form})
    
class CouponApplyView(LoginRequiredMixin, View):
    form_class = CouponApplyForm
    
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
    
    def dispatch(self, request, order_id, *args, **kwargs):
        self.order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user,
            status=Order.Status.WAITING_FOR_ADDRESS
        )
        return super().dispatch(request, *args, **kwargs)

    
    def get(self, request):        
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form, 'order': self.order})
    
    def post(self, request):
        form = self.form_class(user=request.user, data=request.POST)
        
        if form.is_valid():
            address_choice = form.cleaned_data['address_choice']
            
            if address_choice == self.form_class.USE_EXISTING_ADDRESS:
                # استفاده از آدرس موجود
                existing_address = form.cleaned_data['existing_address']
                self.order.order_address = existing_address
            
            else:
                address = Address.objects.create(
                    user=request.user,
                    province=form.cleaned_data['new_province'],
                    city=form.cleaned_data['new_city'],
                    postal_code=form.cleaned_data['new_postal_code'],
                    address=form.cleaned_data['new_address'],
                    plaque=form.cleaned_data['new_plaque'],
                    unit=form.cleaned_data['new_unit'],
                    receiver_first_name=form.cleaned_data['new_receiver_first_name'],
                    receiver_last_name=form.cleaned_data['new_receiver_last_name'],
                    receiver_phone=form.cleaned_data['new_receiver_phone'],
                )
                
                if form.cleaned_data['save_new_address']:
                    address.is_active = True
                    address.save()
                
                self.order.order_address = address
                
            # 🔥 تغییر وضعیت
            self.order.status = Order.Status.WAITING_FOR_PAYMENT
            
            self.order.address_submitted_at = tz.now()
            self.order.save()
            
            messages.success(request, 'آدرس با موفقیت ثبت شد', 'success')
            return redirect('orders:select_payment', order_id=self.order.id)        
        return render(request, self.template_name, {'form': form, 'order': self.order})

class SelectPaymentMethodView(LoginRequiredMixin, View):
    form_class = PaymentMethodForm
    template_name = 'orders/select_payment.html'

    def dispatch(self, request, order_id, *args, **kwargs):
        self.order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user,
            status=Order.Status.WAITING_FOR_PAYMENT
        )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {
            'order': self.order,
            'form': form
        })

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            self.order.payment_type = form.cleaned_data['payment_type']

            if self.order.payment_type == 'cash':
                self.order.status = Order.Status.PENDING
                self.order.save()
                return redirect('payments:start', self.order.id)

            self.order.status = Order.Status.WAITING_APPROVAL
            self.order.save()
            return redirect('orders:installment_waiting', self.order.id)

        return render(request, self.template_name, {
            'order': self.order,
            'form': form
        })
    
    
class InstallmentWaitingView(TemplateView):
    template_name = 'orders/installment_waiting.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        context['order'] = Order.objects.get(id=order_id, user=self.request.user)
        return context
    
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
        order.paid_at = tz.now()
        order.save(using= self._db)

        messages.success(request, 'پرداخت با موفقیت انجام شد. سفارش شما ثبت شد.', 'success')
        return redirect('orders:order_detail', order_id=order.id)
    
class CashPaymentView(View):
    def get(self, request, order_id):
        order = Order.objects.get(id=order_id, user=request.user)
        if order.status != Order.Status.PENDING:
            # اگر هنوز pending نشده، اجازه پرداخت ندیم
            return redirect('orders:select_payment', order_id=order.id)

        # اینجا میتونی به درگاه بانکی متصل بشی
        # برای تست:
        return redirect('orders:payment_success', order_id=order.id)   
    
class PaymentSuccessView(View):
    def get(self, request, order_id):
        order = Order.objects.get(id=order_id, user=request.user)
        if order.status != Order.Status.PENDING:
            # اگر هنوز pending نشده، اجازه پرداخت ندیم
            return redirect('orders:select_payment', order_id=order.id)

        # اینجا میتونی به درگاه بانکی متصل بشی
        # برای تست:
        return redirect('orders:payment_success', order_id=order.id)