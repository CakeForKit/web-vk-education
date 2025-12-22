from django import forms
from django.contrib.auth.models import User

from app.models import Profile, Question, Tag, Answer


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Login")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

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
            'accept' : 'image/*',
            'class'  : "form-control",
            'id': 'avatarUpload',
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
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data['password']
        password2 = cleaned_data['password2']
        if password and password2 and password != password2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data
    
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
        
        if avatar:
            profile = Profile.objects.create(
                user=user, 
                nickname=nickname,
                avatar=avatar
            )
        else:
            profile = Profile.objects.create(
                user=user, 
                nickname=nickname
            )
        profile.save()
        return user
    
class ProfileEditForm(forms.Form):
    username        = forms.CharField(max_length=100, label="Login")
    email           = forms.EmailField(label="Email")
    nickname        = forms.CharField(max_length=100, label="NickName")
    password        = forms.CharField(widget=forms.PasswordInput, label="Password", required=False)
    password2       = forms.CharField(widget=forms.PasswordInput, label="Confirm Password", required=False)
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
    
    def save(self):
        print(self.cleaned_data)
        
        self.profile.user.username = self.cleaned_data['username']
        self.profile.user.email = self.cleaned_data['email']
        self.profile.nickname = self.cleaned_data['nickname']
        if self.cleaned_data['avatar']:
            self.profile.avatar = self.cleaned_data['avatar']

        password = self.cleaned_data.get('password')
        if password:
            self.profile.user.set_password(password)

        self.profile.user.save()
        self.profile.save()
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if username != self.profile.user.username and \
            User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if email != self.profile.user.email and \
            User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data
    

class QuestionForm(forms.Form):
    title = forms.CharField(max_length=100, label="Title")
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), label="Text")
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), label="Tags", required=False)

    def __init__(self, profile, *args, **kwargs):
        self.profile = profile
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['tags'].widget.attrs['title'] = 'Hold Ctrl/Cmd to select multiple tags'
        self.fields['tags'].widget.attrs['size'] = '6'

    def save(self):
        title = self.cleaned_data['title']
        text = self.cleaned_data['text']
        tags = self.cleaned_data['tags']

        question = Question.objects.create(
            title=title,
            text=text,
            user=self.profile  
        )
        question.save()
        question.mm_tags.set(tags)
        return question
    
class AnswerForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(), label="Text")

    def __init__(self, question, profile, *args, **kwargs):
        self.question = question
        self.profile = profile
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs = {
            'class': 'form-control',
            'rows': 3,
            'placeholder' : 'Enter your answer here...',
        }

    def save(self):
        text = self.cleaned_data['text']

        answer = Answer.objects.create(
            question=self.question,
            text=text,
            user=self.profile  
        )
        return answer