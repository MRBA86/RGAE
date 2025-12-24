from django.contrib import admin
from website.models import Contact , Newsletter, Cooperateus, Project, ProjectImages

class ContactAdmin(admin.ModelAdmin):
    ordering = ['created_date']
    list_display = ('name', 'email', 'created_date', 'updated_date')
    list_filter = ('email',)
    search_fields = ['name', 'message', 'subject']
    empty_value_display = 'خالی'
    
    
class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ("title",)}

admin.site.register(Contact,ContactAdmin)
admin.site.register(Newsletter)
admin.site.register(Cooperateus)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectImages)

# Register your models here.
