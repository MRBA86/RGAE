from django.db import models
from django.urls import reverse
from accounts.models import User
from taggit.managers import TaggableManager
from utils import slugify_farsi
import django_jalali.db.models as jmodels

# Create your models here.
class Category(models.Model):
    name = models.CharField(verbose_name = "نام دسته بندی", max_length=255)
    slug = models.SlugField(verbose_name = "اسلاگ دسته بندی", max_length=255, unique=True, allow_unicode=True)
    
    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_farsi(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category-filter", args=[self.slug])    
    
    
class Post(models.Model):
    author = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name = "نویسنده") 
    image = models.ImageField(verbose_name = "تصویر پست", upload_to='blog/%Y%m%d/',default='blog/default.jpg')
    title = models.CharField(verbose_name = "عنوان پست", max_length=255)
    slug = models.SlugField(verbose_name = "اسلاگ پست", max_length=255, unique=True, allow_unicode=True)
    tags = TaggableManager(verbose_name = "تگ های پست", blank=True)
    category = models.ManyToManyField(Category, verbose_name = "دسته بندی پست",)
    content = models.TextField(verbose_name = "متن پست")
    counted_views = models.IntegerField(verbose_name = "تعداد بازدید", default=0)
    created_date = jmodels.jDateTimeField(verbose_name = "تاریخ ایجاد", auto_now_add=True)
    updated_date = jmodels.jDateTimeField(verbose_name = "تاریخ ویرایش", auto_now=True)
    status = models.BooleanField(verbose_name = "وضعیت پست", default=False)
    published_date = jmodels.jDateTimeField(verbose_name = "تاریخ انتشار", null=True)
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = 'پست'
        verbose_name_plural = 'پست ها'

    def __str__(self):
        return "{} - {} ".format(self.title,self.id)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_farsi(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("blog:post-detail", args=[self.slug])
    
    
    
