from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager
import django_jalali.db.models as jmodels

class User(AbstractBaseUser):
    
    class Genders(models.TextChoices):
        MALE = 'مرد'
        FEMALE = 'زن'
        
    email = models.EmailField(verbose_name="آدرس ایمیل", max_length=255, unique=True)
    phone_number = models.CharField(verbose_name="شماره تلفن", max_length=11 , unique=True)
    image = models.ImageField(upload_to='User/%Y%m%d/',default='User/default.jpg')
    first_name = models.CharField(verbose_name="نام", max_length=58)
    last_name = models.CharField(verbose_name="نام خانوادگی", max_length=128)
    gender = models.CharField(verbose_name="جنسیت", max_length=12, choices=Genders.choices, default='مرد')
    national_id = models.CharField(verbose_name="شماره ملی", max_length=10, unique=True)
    birth_date = jmodels.jDateField(verbose_name="تاریخ تولد", blank=True, null=True)
    is_active = models.BooleanField(verbose_name="فعال هست ؟", default=True)
    is_admin = models.BooleanField(verbose_name="ادمین هست ؟", default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ['email','national_id']
    
    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin
    
    def __str__(self):
        return f'{self.email} - {self.phone_number}'
    
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
        
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'    
    
    
class OtpCode(models.Model):
    
    phone_number = models.CharField(verbose_name="شماره تلفن", max_length=11)
    code = models.PositiveSmallIntegerField(verbose_name="کد یکبار مصرف")
    created = jmodels.jDateTimeField(verbose_name="تاریخ ایجاد", auto_now=True)   


    def __str__(self):
        return f' {self.phone_number} - {self.code} - {self.created}'

    class Meta:
        verbose_name = 'کد یکبار مصرف'
        verbose_name_plural = 'کدهای یکبار مصرف' 
    
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(verbose_name="عنوان آدرس", max_length=100, help_text='مثال: خانه، محل کار، و...')
    province = models.CharField(verbose_name='استان', max_length=100)
    city = models.CharField(verbose_name="شهر", max_length=100)
    address = models.TextField(verbose_name='آدرس کامل')
    postal_code = models.CharField(max_length=10)
    plaque = models.CharField(verbose_name='پلاک', max_length=10)
    unit = models.CharField(verbose_name='واحد', max_length=10, blank=True)   
    # اطلاعات گیرنده
    receiver_first_name = models.CharField(verbose_name='نام گیرنده', max_length=100)
    receiver_last_name = models.CharField(verbose_name='نام خانوادگی گیرنده', max_length=100)
    receiver_phone = models.CharField(verbose_name='تلفن گیرنده', max_length=11)
    # وضعیت‌ها
    is_default = models.BooleanField(verbose_name='آدرس پیش‌فرض', default=False)
    is_active = models.BooleanField(verbose_name='فعال', default=True)
    created_at = jmodels.jDateTimeField( auto_now_add=True )
    updated_at = jmodels.jDateTimeField( auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name = 'آدرس'
        verbose_name_plural = 'آدرس‌ها'
    
    def __str__(self):
        return f"{self.title} - {self.city}"
    
    def get_full_address(self):
        """دریافت آدرس کامل"""
        return f"{self.province}، {self.city}، {self.address}"
    
    def get_full_name_reciever(self):
        return f"{self.receiver_first_name} {self.receiver_last_name}"
