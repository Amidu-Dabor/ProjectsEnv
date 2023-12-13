from dataclasses import fields
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Ticket, Comment


class UserCreateForm(UserCreationForm, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['photo', 'uid', 'user_name', 'first_name', 'last_name', 'department', 'email', 'password1',
                  'password2']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['photo', 'user_name', 'first_name', 'last_name', 'biography', 'password']


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = '__all__'
        exclude = ['creator', 'contributors']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
