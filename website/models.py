from django.db import models
from django.urls import reverse
from utils import slugify_farsi
import django_jalali.db.models as jmodels

class Contact(models.Model):
    name = models.CharField(verbose_name="نام", max_length=50)
    email = models.EmailField(verbose_name="آدرس ایمیل",)
    message = models.TextField(verbose_name="متن پیام",)
    created_date = jmodels.jDateTimeField(verbose_name="تاریخ ایجاد", auto_now_add=True)
    updated_date = jmodels.jDateTimeField(verbose_name="تاریخ ویرایش", auto_now=True)
    
    
    class Meta:
        verbose_name = "مخاطب"
        verbose_name_plural = "مخاطبین"
        
        
    def __str__(self):
        return f'{self.name} - {self.email}'
    
class Newsletter(models.Model):
    email = models.EmailField(verbose_name = "آدرس ایمیل")

    class Meta:
        verbose_name = "خبرنامه"
        verbose_name_plural = "اخبارنامه"
        

    def __str__(self):
        return self.email

class Cooperateus(models.Model):
    
    class Genders(models.TextChoices):
        MALE = 'مرد'
        FEMALE = 'زن'
    
    class Maritials(models.TextChoices):
        SINGLE = 'مجرد'    
        MARRIED = 'متاهل'
        
    first_name = models.CharField(verbose_name="نام", max_length=64)
    last_name = models.CharField(verbose_name="نام خانوادگی",max_length=100)
    phone_number = models.CharField(verbose_name="شماره تلفن",max_length=11)
    email = models.EmailField(verbose_name="پست الکترونیکی")
    age = models.PositiveSmallIntegerField(verbose_name="سن",)
    marital_status = models.CharField(verbose_name="وضعیت تاهل", max_length=12, choices=Maritials.choices)
    gender = models.CharField(verbose_name="جنسیت", max_length=12, choices=Genders.choices)
    education = models.CharField(verbose_name="تحصیلات",max_length=50)
    description = models.TextField(verbose_name="توضیحات",)
    cv = models.FileField(verbose_name="رزومه", upload_to="CV/%Y-%m-%d/")
    created_at = jmodels.jDateTimeField(verbose_name="تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField(verbose_name="تاریخ ویرایش", auto_now=True)
    
    class Meta:
        verbose_name = 'درخواست همکاری'
        verbose_name_plural = 'درخواست های همکاری'
    
    def __str__(self):
        return f'{self.phone_number} - {self.last_name} - {self.created_at}'



class Project(models.Model):
    
    title = models.CharField(verbose_name="عنوان ", max_length=255) 
    slug = models.SlugField(verbose_name="اسلاگ ", max_length=255, unique=True, allow_unicode=True)
    content = models.TextField(verbose_name="محتوا پروژه ")
    created_date = jmodels.jDateTimeField(verbose_name="تاریخ ایجاد ", auto_now_add=True)
    updated_date = jmodels.jDateTimeField(verbose_name="تاریخ ویرایش ", auto_now=True)
    status = models.BooleanField(verbose_name="وضعیت ", default=False)
    published_date = jmodels.jDateTimeField(verbose_name="تاریخ انتشار ", null=True) 
    
    class Meta:
        
        verbose_name = "پروژه"
        verbose_name_plural = "پروژه ها"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_farsi(self.title)
        super().save(*args, **kwargs)   
    
    @property
    def primary_image(self):
        """دریافت تصویر اصلی پروژه"""
        try:
            return self.images.get(is_primary=True)
        except ProjectImages.DoesNotExist:
            return self.images.first()
    
    @property
    def all_images(self):
        """دریافت تصاویر پروژه"""
        return self.images.all()
    
    def __str__(self):
        return f'{self.title} - {self.created_date}'
    
    def get_absolute_url(self):
        return reverse("website:project_detail", args=[self.slug])
    
class ProjectImages(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images', verbose_name="پروژه ")
    name = models.CharField(max_length=50, verbose_name="تصویر ")
    image = models.ImageField(upload_to='Project/images/%Y%m%d/')
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="متن جایگزین")
    is_primary = models.BooleanField(default=False, verbose_name="تصویر اصلی")
    created_at = jmodels.jDateTimeField(verbose_name="تاریخ ایجاد ", auto_now_add=True)
    updated_at = jmodels.jDateTimeField(verbose_name="تاریخ ویرایش ", auto_now=True)
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
        verbose_name = "تصویر پروژه"
        verbose_name_plural = "تصاویر پروژه"
    
    
    def __str__(self):
        return f'{self.name} - {self.project} - {self.created_at}'
        