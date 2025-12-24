from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import UserRegisterationForm, VerifyCodeForm, UserLoginForm, AddressForm
from utils import send_otp_code
import random
from django.contrib import messages
from .models import User, OtpCode, Address
from orders.models import Order
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


class UserRegisterView(View):
    form_class = UserRegisterationForm
    template_name = 'accounts/register.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('website:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form' : form})
        
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            random_code = random.randint(1000,9999)
            send_otp_code(form.cleaned_data['phone_number'], random_code)
            OtpCode.objects.create(phone_number=form.cleaned_data['phone_number'], code= random_code)
            request.session['user_registration_info'] = {
                'phone_number' : form.cleaned_data['phone_number'] ,
                'email' : form.cleaned_data['email'],
                'national_id' : form.cleaned_data['national_id'],
                'password' : form.cleaned_data['password'],
            }
            messages.success(request, 'ما یک کد تایید برای شما ارسال کردیم', 'success')
            return redirect('accounts:verify_code')
        return render(request, self.template_name, {'form': form})

class UserRegisterVerifyCodeView(View):
    form_class = VerifyCodeForm
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('website:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        user_session = request.session['user_registration_info']
        
        form = self.form_class
        return render(request, 'accounts/verify.html', {'form':form, 'phone_number': user_session['phone_number']})
    
    def post(self, request):
        user_session = request.session['user_registration_info']
        code_instance = OtpCode.objects.get(phone_number=user_session['phone_number'])
        form = self.form_class(request.POST)
        print(code_instance)
        if form.is_valid():
            cd = form.cleaned_data
            print(cd)
            print(code_instance)
            if cd['code'] == code_instance.code :
                User.objects.create_user(user_session['phone_number'], user_session['email'],
                                         user_session['national_id'], user_session['password'])
                code_instance.delete()
                messages.success(request, 'ثبت نام شما با موفقیت انجام شد', 'success')
                return redirect('website:home')
            else:
                print(code_instance)
                print(cd['code'])
                messages.error(request, ' کد وارد شده اشتباه است', 'danger')
                return redirect('accounts:verify_code')
        return redirect('website:home')
    
    
class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    
    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('website:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})
    
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username= cd['phone_number'], password= cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'ورود شما با موفقیت انجام شد','success')
                if self.next:
                    return redirect(self.next)
                return redirect('website:home')
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است', 'warning')
            return render(request, self.template_name, {'form': form})
        
        
        
class UserLogoutView(LoginRequiredMixin, View):
    
    def get(self, request):
        logout(request)
        messages.success(request, 'شما با موفقیت از حساب کاربری خود خارج شدید', 'success')
        return redirect('website:home')
    
    
class UserProfileView(LoginRequiredMixin, View):
    
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        user_orders = Order.objects.filter(user=user).order_by('-created_at')
        return render(request, 'accounts/user_profile.html', {'user': user, 'user_orders': user_orders})

class UserAddressView(LoginRequiredMixin, View):
    
    def get(self, request):
        user_addresses = Address.objects.filter(user=request.user , is_active=True)
        return render(request, 'accounts/user_addresses.html', {'user_addresses': user_addresses})

    
class UserDetailsView(LoginRequiredMixin, View):
    def get(self, request):
        pass
    
    def post(self, request):
        pass

class AddressCreateView(LoginRequiredMixin, View):
    """ایجاد آدرس جدید"""
    form_class = AddressForm
    template_name = 'accounts/address_form.html'
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # اگر اولین آدرس است، آن را پیش‌فرض کن
            if not Address.objects.filter(user=request.user).exists():
                address.is_default = True
            
            address.save()
            messages.success(request, 'آدرس جدید با موفقیت اضافه شد', 'success')
            return redirect('accounts:user_addresses')
        
        return render(request, self.template_name, {'form': form})  
    
class AddressUpdateView(LoginRequiredMixin, View):
    """ویرایش آدرس"""
    
    def get(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        form = AddressForm(instance=address)
        return render(request, 'accounts/address_form.html', {'form': form})
    
    def post(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'آدرس با موفقیت به‌روزرسانی شد')
            return redirect('accounts:address_list')
        
        return render(request, 'accounts/address_form.html', {'form': form})

class AddressDeleteView(LoginRequiredMixin, View):
    """حذف آدرس (غیرفعال کردن)"""
    
    def post(self, request, address_id):
        address = get_object_or_404(Address, pk=address_id, user=request.user)
        
        # به جای حذف فیزیکی، غیرفعال می‌کنیم
        address.is_active = False
        address.save()
        
        # اگر آدرس پیش‌فرض بود، یک آدرس دیگر را پیش‌فرض کن
        if address.is_default:
            other_address = Address.objects.filter(user=request.user, is_active=True).first()
            if other_address:
                other_address.is_default = True
                other_address.save()
        
        messages.success(request, 'آدرس با موفقیت حذف شد')
        return redirect('accounts:user_addresses')

class SetDefaultAddressView(LoginRequiredMixin, View):
    """تنظیم آدرس به عنوان پیش‌فرض"""
    
    def post(self, request, address_id):
        address = get_object_or_404(Address, pk=address_id, user=request.user)
        
        # تمام آدرس‌های کاربر را از حالت پیش‌فرض خارج کن
        Address.objects.filter(user=request.user).update(is_default=False)
        
        # این آدرس را پیش‌فرض کن
        address.is_default = True
        address.save()
        
        messages.success(request, 'آدرس پیش‌فرض تغییر کرد', 'success')
        return redirect('accounts:user_addresses')
 
    
class UserOrdersView(LoginRequiredMixin, View):
    
    def get(self, request):
        user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'orders/user_orders.html', {'user_orders': user_orders} )
    
class UserPasswordResetView(auth_views.PasswordResetView):
    
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('accounts:password_reset_done') 
    email_template_name = 'accounts/password_reset_email.html'  
    

class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'
    
    
class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name ='accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    
class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'