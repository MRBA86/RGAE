from django import forms
from .models import User, Address
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='رمز عبور',widget=forms.PasswordInput)
    password2 = forms.CharField(label='تایید رمزعبور',widget=forms.PasswordInput)
    
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] and cd['password2'] and cd['password1'] != cd['password2']:
            raise ValidationError('رمز عبور یکسان نمی باشند')
        return cd['password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            
        return user
            
    class Meta:
        model = User
        fields = ('email', 'phone_number', 'national_id')
        
class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text="You Can Change Password From <a href=\"../password/\"> This Form </a>.")
    
    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password', 'image', 'first_name', 'last_name', 'birth_date', 'gender','national_id', 'is_active', 'is_admin', 'last_login']

class UserUpdateDetailsForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password', 'image', 'first_name', 'last_name', 'birth_date', 'gender','national_id']
        
class UserRegisterationForm(forms.Form):
        
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=128)
    phone_number = forms.CharField(max_length=11)
    email = forms.EmailField()
    national_id = forms.CharField(max_length=10)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email= email).exists()
        if user :
            raise ValidationError('آدرس ایمیل موجود می باشد')  
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        user = User.objects.filter(phone_number=phone_number).exists()
        if user :
            raise ValidationError('شماره موبایل وارده موجود می باشد')
        return phone_number
    
    def clean_national_id(self):
        national_id = self.cleaned_data['national_id']
        user = User.objects.filter(national_id=national_id).exists()
        if user :
            raise ValidationError('کد ملی وارده موجود می باشد')
        return national_id
    
class UserProfileInfoForm(forms.ModelForm):
    
      class Meta:
        model = User
        fields = ['email', 'phone_number', 'image', 'first_name', 'last_name', 'birth_date', 'gender','national_id']
       
    
class VerifyCodeForm(forms.Form):
    code = forms.IntegerField()
    
class UserLoginForm(forms.Form):
    phone_number = forms.CharField(max_length=11, required=True)
    password = forms.CharField(widget=forms.PasswordInput)


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'title', 'province', 'city', 'postal_code',
            'address', 'plaque', 'unit',
            'receiver_first_name', 'receiver_last_name',
            'receiver_phone'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'title': 'عنوان آدرس',
            'province': 'استان',
            'city': 'شهر',
            'postal_code': 'کد پستی',
            'address': 'آدرس کامل',
            'plaque': 'پلاک',
            'unit': 'واحد',
            'receiver_first_name': 'نام گیرنده',
            'receiver_last_name': 'نام خانوادگی گیرنده',
            'receiver_phone': 'تلفن گیرنده',
        }