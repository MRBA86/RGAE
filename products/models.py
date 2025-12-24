from django.db import models
from django.urls import reverse
from utils import slugify_farsi
import django_jalali.db.models as jmodels

class Category(models.Model):
    name = models.CharField(verbose_name='نام دسته بندی', max_length=200)
    slug = models.SlugField(verbose_name='اسلاگ',max_length=255, unique=True, allow_unicode=True)
    
            
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_farsi(self.title)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'
        
    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="دسته بندی ")
    title = models.CharField(verbose_name='عنوان محصول', max_length=200)
    name = models.CharField(verbose_name='نام محصول', max_length=200)
    product_code = models.CharField(verbose_name='کد محصول', unique=True)
    slug = models.SlugField(verbose_name='اسلاگ محصول',max_length=255, unique=True, allow_unicode=True)
    product_brand =models.CharField(verbose_name='برند محصول', max_length=200)
    description = models.TextField(verbose_name='توضیحات محصول',)
    price = models.IntegerField(verbose_name='قیمت محصول',)
    available = models.BooleanField(verbose_name='وضعیت فعال محصول',)
    created = jmodels.jDateTimeField(verbose_name="تاریخ ایجاد ", auto_now_add=True)
    updated = jmodels.jDateTimeField(verbose_name="تاریخ ویرایش ", auto_now=True)
    
    @property
    def primary_image(self):
        """دریافت تصویر اصلی محصول"""
        try:
            return self.images.get(is_primary=True)
        except ProductImage.DoesNotExist:
            return self.images.first()
    
    @property
    def all_images(self):
        """دریافت تصاویر محصول"""
        return self.images.all()
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        
    
    def __str__(self):
        return f'{self.name} - {self.created}'
            
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_farsi(self.title)
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse("products:product_detail", args=[self.slug])
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/%Y%m%d/', verbose_name="تصویر محصول")
    alt_text = models.CharField(verbose_name='توضیحات تصویر',max_length=200)
    is_primary = models.BooleanField(verbose_name='تصویر اصلی',default=False)
    created_at = jmodels.jDateTimeField(auto_now_add=True)
    updated_at = jmodels.jDateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('-is_primary','created_at')
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصول'
    
    def __str__(self):
        return f"Image For {self.product.name}"
    
    
class Modem(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='modems')
    color = models.CharField(verbose_name='رنگ', max_length=50)
    lan_port = models.IntegerField(verbose_name='تعداد پورت شبکه')
    lan_speed = models.CharField(verbose_name='سرعت پورت شبکه',max_length=50)
    anten_power = models.IntegerField(verbose_name='قدرت آنتن')
    anten_quantity = models.IntegerField(verbose_name='تعداد آنتن')
    tel_quantity = models.IntegerField(verbose_name='تعداد پورت تلفن')
    usb_quantity = models.IntegerField(verbose_name='تعداد پورت USB')
    wifi_technology = models.CharField(verbose_name='تکنولوژی Wifi', max_length=50)
    wifi_speed = models.IntegerField(verbose_name='سرعت وایرلس')
    wifi5_speed = models.IntegerField(verbose_name='سرعت وایرلس باند 5')
    pon = models.CharField(verbose_name='PON', max_length=50)
    two_bands = models.BooleanField(verbose_name='دو بانده')
    created_at = jmodels.jDateTimeField(auto_now_add=True)
    updated_at = jmodels.jDateTimeField(auto_now=True)    

    class Meta:
        ordering = ('wifi_technology','created_at')
        verbose_name = 'ویژگی محصول'
        verbose_name_plural = 'ویژگی های محصول'
    
    def __str__(self):
        return f"Options For {self.product.name}"
        
    
    
