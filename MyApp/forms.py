from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm



class BaseStyle(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for i_name, i in self.fields.items():
            i.widget.attrs['class']='form-control'



class RegisterForm(UserCreationForm):
    class Meta:
        model = UserModel
        fields = ['username', 'email', 'password1', 'password2']
        
        
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for i_name, i in self.fields.items():
            i.widget.attrs['class']='form-control'
        

class AuthForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['username',  'password',]
        
        
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for i_name, i in self.fields.items():
            i.widget.attrs['class']='form-control'


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control bg-dark text-light border-secondary py-2',
                'placeholder': field.label
            })




class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'inquiry_type', 'order_number', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (e.g. 017xxxxxxxx)'}),
            'inquiry_type': forms.Select(attrs={'class': 'form-select'}),
            'order_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Order ID (Optional)'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'How can we help you?'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your message in detail...', 'style': 'height: 150px;'}),
        }


