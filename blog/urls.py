from django.urls import path, re_path
from .views import PostsView, PostDetailView

app_name = 'blog'

urlpatterns = [
    path('', PostsView.as_view(), name="posts"),
    re_path(r'category/(?P<category_slug>[-\w\u0600-\u06FF]+)/$', PostsView.as_view(), name='category-filter'),
    #path('<int:post_id>/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    re_path(r'(?P<slug>[-\w\u0600-\u06FF]+)/$', PostDetailView.as_view(), name='post-detail'),
]
