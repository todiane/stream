# profiles/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class BaseForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50'
            })
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'rows': '4',
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50'
                })

class UserRegisterForm(BaseForm, UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom labels and help texts
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter your password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm your password'})

class UserUpdateForm(BaseForm, forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'})
        }

class ProfileUpdateForm(BaseForm, forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Tell us about yourself'})
    )

    class Meta:
        model = Profile
        fields = ['first_name', 'bio']

from django import forms
from .models import ContactSubmission

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ['reason', 'name', 'description', 'parent_first_name', 
                 'parent_last_name', 'parent_email', 'parent_phone']
        
    def clean(self):
        cleaned_data = super().clean()
        reason = cleaned_data.get('reason')
        
        if reason == 'tuition':
            required_fields = ['parent_first_name', 'parent_last_name', 
                             'parent_email', 'parent_phone']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for tuition enquiries')
                    
        return cleaned_data
