from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .forms import UserCreationForm, UserChangeForm
from .models import User, OtpCode

@admin.register(OtpCode)
class OtpAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'created')
    
    
class UserAdmin(BaseUserAdmin):
    
    form = UserChangeForm
    add_form = UserCreationForm
    
    list_display = ('email', 'national_id', 'phone_number', 'is_admin')
    list_filter = ('email', 'phone_number', 'national_id')
    fieldsets = (
        (None, {'fields': ('email','phone_number', 'national_id','password', 'first_name', 'last_name', 'birth_date')}),
        ('Permission', {'fields': ('is_active', 'is_admin', 'last_login')}),
        
    )
    
    add_fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'national_id', 'password1', 'password2', 'birth_date')}),
    )
    search_fields = ('email', 'phone_number', 'national_id')
    ordering = ('email',)
    filter_horizontal = ()
    
    
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
# Register your models here.
