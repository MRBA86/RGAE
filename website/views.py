from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.views.generic import ListView
from .forms import ContactForm, NewsletterForm, CooperateUsForm
from .models import Project, ProjectCategory
from blog.models import Post
from products.models import Product
from django.db.models import F

class HomeView(View):
    
    def get(self, request):
        projects = Project.objects.filter(status=True)[:4]
        products = Product.objects.all()
        posts = Post.objects.all()[:4]

        return render(request, 'website/home.html', {'projects': projects, 'products': products, 'posts': posts})
    
class AboutUsView(View):
    def get(self, request):
        return render(request, 'website/aboutus.html')
    
class ContactUsView(View):
    
    form_class = ContactForm
    template_class = 'website/contactus.html'
    
    def get(self, request):
        form = self.form_class
        return render(request, self.template_class, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            #send Email
            messages.success(request, 'پیام شما با موفقیت ثبت شد', 'success')
        return redirect('website:contact-us')
    
class NewsLetterView(View):
    
    form_class = NewsletterForm
    
    def get(self, request):
        form = self.form_class
        return render(request, 'website:newsletter', {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'درخواست شما با موفقیت ثبت شد', 'success')
        return redirect('website:home')
    
class CooperateWithUSView(View):

    form_class = CooperateUsForm
    template_name = 'website/cooperate-us.html'
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            try:
                print(form.cleaned_data)
                form.save()
                messages.success(request, 'درخواست شما با موفقیت ارسال گردید', 'success')
            except Exception as e:
                messages.error(request, f'خطا در ذخیره اطلاعات: {str(e)}', 'error')
        messages.error(request, 'درخواست شما ارسال نشد', 'warning')
        return redirect('website:cooperate-us')
    

class ProjectListView(ListView):
    model = Project
    template_name = 'website/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        queryset = Project.objects.filter(status=True)

        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(ProjectCategory, slug=category_slug)
            queryset = queryset.filter(category=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProjectCategory.objects.all()
        return context

   
class ProjectDetailView(View):
    
    def get(self, request, slug):
        latest_projects = Project.objects.filter(status=True).order_by('-published_date')[:4]
        project = get_object_or_404(Project, slug=slug)
        images = project.all_images
        primary_image = project.primary_image
        # افزایش امن تعداد بازدید
        Project.objects.filter(pk=project.pk).update(counted_views=F('counted_views') + 1 )

        # گرفتن مقدار جدید برای نمایش
        project.refresh_from_db()
        return render(request, 'website/project_detail.html', {'project':project , 'images': images, 'primary_image': primary_image, 'latest_projects':latest_projects})