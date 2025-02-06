from django import forms
from .models import Student
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.core.exceptions import ValidationError

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'phone', 'email', 'password']

class EssayForm(forms.Form):
    essay_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 10,  # Set the number of visible text lines
            'cols': 80,  # Set the width of the textarea
            'placeholder': 'Write your essay here...'  # Optional placeholder text
        }),
        label='Essay Text'
    )

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class UpdatePreferencesForm(forms.ModelForm):
    class Meta:
        model = Profile  # Assuming you have a Profile model for user preferences
        fields = ['ai_voice']
        widgets = {
            'ai_voice': forms.Select(attrs={'class': 'form-control'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['picture']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email
    
class UpdatePreferencesForm(forms.ModelForm):
    class Meta:
        model = Profile  # Assuming you have a Profile model for user preferences
        fields = ['ai_voice']  # Make sure 'ai_voice' is included here
        widgets = {
            'ai_voice': forms.Select(attrs={'class': 'form-control'}),
        }


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['picture']