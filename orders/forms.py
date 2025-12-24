from django import forms
from accounts.models import Address

class CartAddForm(forms.Form):
    quantity = forms.IntegerField(min_value=1 , max_value=10)
    


class OrderAddressForm(forms.Form):
    USE_EXISTING_ADDRESS = 'existing'
    USE_NEW_ADDRESS = 'new'
    
    ADDRESS_CHOICE = [
        (USE_EXISTING_ADDRESS, 'استفاده از آدرس ذخیره شده'),
        (USE_NEW_ADDRESS, 'وارد کردن آدرس جدید'),
    ]
    
    address_choice = forms.ChoiceField( choices=ADDRESS_CHOICE, widget=forms.RadioSelect,
                                       initial=USE_EXISTING_ADDRESS, label='نحوه ارسال')
    
    existing_address = forms.ModelChoiceField(queryset=Address.objects.none(),  # در __init__ پر می‌شود
                                        required=False, label='انتخاب آدرس', widget=forms.RadioSelect)
    
    # فیلدهای آدرس جدید
    new_title = forms.CharField( max_length=100, required=False, label='عنوان آدرس',
                                help_text='مثال: خانه، محل کار' )
    
    new_province = forms.CharField(max_length=100, required=False, label='استان')
    
    new_city = forms.CharField(max_length=100, required=False, label='شهر')
    
    new_postal_code = forms.CharField(max_length=10, required=False, label='کد پستی')
    
    new_address = forms.CharField( widget=forms.Textarea(attrs={'rows': 3}),
                                  required=False, label='آدرس کامل')
    
    new_plaque = forms.CharField(max_length=10, required=False, label='پلاک')
    
    new_unit = forms.CharField(max_length=10, required=False, label='واحد')
    
    new_receiver_first_name = forms.CharField(max_length=100, required=False, label='نام گیرنده')
    
    new_receiver_last_name = forms.CharField(max_length=100, required=False, label='نام خانوادگی گیرنده')
    
    new_receiver_phone = forms.CharField(max_length=11, required=False, label='تلفن گیرنده')
    
    save_new_address = forms.BooleanField(required=False, initial=True, 
                                          label='ذخیره این آدرس در پروفایل من')
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if user:
            # فقط آدرس‌های فعال کاربر را نشان بده
            self.fields['existing_address'].queryset = Address.objects.filter(user=user, is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        address_choice = cleaned_data.get('address_choice')
        
        if address_choice == self.USE_EXISTING_ADDRESS:
            # بررسی اینکه آدرس موجود انتخاب شده
            if not cleaned_data.get('existing_address'):
                self.add_error('existing_address', 'لطفاً یک آدرس انتخاب کنید')
        
        elif address_choice == self.USE_NEW_ADDRESS:
            # اعتبارسنجی فیلدهای آدرس جدید
            required_fields = [
                'new_province', 'new_city', 'new_postal_code',
                'new_address', 'new_receiver_first_name',
                'new_receiver_last_name', 'new_receiver_phone'
            ]
            
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'این فیلد الزامی است')
        
        return cleaned_data