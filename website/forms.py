from django import forms
from .models import Contact, Newsletter, Cooperateus


class ContactForm(forms.ModelForm):
    
    class Meta:
        model = Contact
        fields = ("name","email","message")
        
class NewsletterForm(forms.ModelForm):
    
    class Meta:
        model = Newsletter
        fields = '__all__'

class CooperateUsForm(forms.ModelForm):
    
    class Meta :
        model = Cooperateus
        fields = '__all__'