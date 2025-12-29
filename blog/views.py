from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Post, Category
from django.views.generic import ListView
from django.db.models import F



class PostsView(ListView):
    model = Post
    template_name = 'blog/posts.html'
    context_object_name = 'posts'
    paginate_by = 12

    def get_queryset(self):
        queryset = Post.objects.filter(status=True)

        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context        


class PostDetailView(View):
    
    def get(self, request, slug):
        latest_posts = Post.objects.filter(status=True).order_by('-published_date')[:4]
        post = get_object_or_404(Post, slug= slug, status=True)
        # افزایش امن تعداد بازدید
        Post.objects.filter(pk=post.pk).update(counted_views=F('counted_views') + 1 )

        # گرفتن مقدار جدید برای نمایش
        post.refresh_from_db()


        return render(request, 'blog/post_detail.html', {'post':post, 'latest_posts': latest_posts})



# Create your views here.
