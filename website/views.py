from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from .forms import ContactForm, NewsletterForm, CooperateUsForm
from .models import Project
from blog.models import Post
from products.models import Product

class HomeView(View):
    
    def get(self, request):
        projects = Project.objects.all()[:4]
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
    
    
class ProjectListView(View):
    
    def get(self, request):
        projects = Project.objects.all()
        return render(request, 'website/project_list.html', {'projects': projects})
    
class ProjectDetailView(View):
    
    def get(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        images = project.all_images
        primary_image = project.primary_image
        return render(request, 'website/project_detail.html', {'project':project , 'images': images, 'primary_image': primary_image})