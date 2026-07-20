from audioop import minmax
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.db.models import CharField
from django.contrib.auth.models import User
from blog.models import *


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'reading_time', 'category']

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError('title must be at least 5 letters.')
        else:
            return title

    def clean_description(self):
        description = self.cleaned_data['description']
        if len(description) < 3 or len(description) > 300:
            raise forms.ValidationError('Description must be 3 to 300 letters.')
        else:
            return description


class TicketForm(forms.Form):
    message = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Text'}))
    name = forms.CharField(max_length=250, required=True)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=True)
    subject = forms.CharField()

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isnumeric():
            raise forms.ValidationError("Phone number must be numeric")
        else:
            return


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'body']
        widgets = {
            'body': forms.Textarea(attrs={'placeholder': 'Write your opinion here'})
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if not name:
            raise forms.ValidationError("Name cannot be empty")
        else:
            return name

    def clean_body(self):
        body = self.cleaned_data['body']
        if not body:
            raise forms.ValidationError("Body cannot be empty")
        else:
            return body

class SearchForm(forms.Form):
    query = forms.CharField()

    def clean_query(self):
        query = self.cleaned_data['query']
        if len(query)<2:
            raise forms.ValidationError('Search item must be at least 2 characters long.')
        else:
            return query

class LoginForm(forms.Form):
    username = forms.CharField(max_length=250, required=True)
    password = forms.CharField(max_length=250, required=True, widget=forms.PasswordInput)

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(max_length=250, widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(max_length=250, widget=forms.PasswordInput, label='Repeat Password')
    class Meta:
        model=User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password2'] != cd['password']:
            raise forms.ValidationError('Passwords do not match!')
        else:
            return cd['password2']

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class AccountEditForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['date_of_birth', 'bio', 'job', 'image_file']
        widgets = {
            'date_of_birth': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%d'),
        }
