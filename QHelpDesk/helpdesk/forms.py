from dataclasses import fields
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User, Ticket, Comment


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['full_name', 'user_name', 'email', 'password1', 'password2']


class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = '__all__'
        exclude = ['creator', 'contributors']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        

class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'full_name', 'user_name','biography','password']
