from django import forms
from django.contrib.auth.models import User

from app.models import Profile, Question


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Login")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


    # def clean_password(self):
    #     password = self.cleaned_data['password']
    #     if username != 'admin':
    #         raise forms.ValidationError('Please enter a valid username.')
    #     return username

    # def clean(self): 
    #     cleaned_data = super().clean()
    #     # if cleaned_data.get('username') == 'admin':
    #     #     raise forms.ValidationError('Please enter a valid username!!!!.')
    #     return cleaned_data
    

class RegisterForm(forms.Form):
    username        = forms.CharField(max_length=100, label="Login")
    email           = forms.EmailField(label="Email")
    nickname        = forms.CharField(max_length=100, label="NickName")
    password        = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2       = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    avatar          = forms.ImageField(label="Avatar", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'avatar':
                field.widget.attrs['class'] = 'form-control'
        self.fields['avatar'].widget.attrs = {
            'accept' : 'image/*'
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean_password2(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password and password2 and password != password2:
            raise forms.ValidationError('Passwords do not match.')
        return password2
    
    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        email = self.cleaned_data['email']
        nickname = self.cleaned_data['nickname']
        avatar = self.cleaned_data['avatar']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()
        profile = Profile.objects.create(
            user=user, 
            nickname=nickname
        )
        if avatar:
            profile.avatar = avatar
        return user
    
class ProfileEditForm(forms.Form):
    username        = forms.CharField(max_length=100, label="Login")
    email           = forms.EmailField(label="Email")
    nickname        = forms.CharField(max_length=100, label="NickName")
    password        = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2       = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    avatar          = forms.ImageField(label="Avatar", required=False)

    def __init__(self, profile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'avatar':
                field.widget.attrs['class'] = 'form-control'
        self.fields['avatar'].widget.attrs = {
            'accept' : 'image/*',
            'class'  : "form-control",
            'id': 'avatarUpload',
        }
        self.fields['password'].required = False
        
        self.profile = profile
        if self.profile:
            self.fields['username'].initial = self.profile.user.username
            self.fields['email'].initial = self.profile.user.email
            self.fields['nickname'].initial = self.profile.nickname
            self.fields['avatar'].initial = self.profile.avatar

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Обновляем данные User
        if self.user:
            self.user.username = self.cleaned_data['username']
            self.user.email = self.cleaned_data['email']
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            if commit:
                self.user.save()
        
        if commit:
            profile.save()
        
        return profile
    