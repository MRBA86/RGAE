from django.urls import path, re_path
from website.views import *
app_name = 'website'

urlpatterns = [
    path('', HomeView.as_view() , name='home'), 
    path('aboutus/', AboutUsView.as_view() , name='about-us'),
    path('contactus/', ContactUsView.as_view() , name='contact-us'),
    path('newsletter', NewsLetterView.as_view(), name='newsletter'),
    path('cooperat-with-us/', CooperateWithUSView.as_view(), name='cooperate-us'),
    path('projects/', ProjectListView.as_view(), name='projects'),
    re_path(r'projects/(?P<slug>[-\w\u0600-\u06FF]+)/$', ProjectDetailView.as_view(), name='project_detail'),  
]
