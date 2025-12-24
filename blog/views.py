from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Post, Category


class PostsView(View):
    
    def get(self, request, category_slug=None):
        posts = Post.objects.filter(status=True)
        categories = Category.objects.all()
        if category_slug:
            category = Category.objects.get(slug=category_slug)
            posts = posts.filter(category=category)
        return render(request, 'blog/posts.html', {'posts': posts, 'categories': categories })
        


class PostDetailView(View):
    
    def get(self, request, slug):
        
        post = get_object_or_404(Post, slug= slug, status=True)
        return render(request, 'blog/post_detail.html', {'post':post})



# Create your views here.
