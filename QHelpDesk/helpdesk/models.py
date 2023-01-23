from email.policy import default
import datetime
from unicodedata import name
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy
from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin, BaseUserManager


# Create your models here.

class CustomAccountManager(BaseUserManager):    
    
    def create_superuser(self, full_name, user_name, email, password, **other_fields):
    
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        
        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be assigned to is_superuser=True.')
        
        return self.create_user(full_name, user_name, email, password, **other_fields)
    
    def create_user(self, full_name, user_name, email, password, **other_fields):
        
        if not email:
            raise ValueError(gettext_lazy('You must provide an email address.'))
        
        email = self.normalize_email(email)
        user = self.model(full_name=full_name, user_name=user_name, email=email, **other_fields)
        user.set_password(password)
        user.save()
        return user


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class User(AbstractUser, PermissionsMixin):
    avatar = models.ImageField(default="avatar.svg", null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    full_name = models.CharField(max_length=70, blank=True)
    user_name = models.CharField(max_length=50, unique=True)
    email = models.EmailField(gettext_lazy('email address'), unique=True)
    start_date = models.DateTimeField(default=timezone.now)
    biography = RichTextField(gettext_lazy('biography'), max_length=500, blank=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    objects = CustomAccountManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'user_name', 'password']
    
    def __str__(self):
        return self.user_name
        
    
class Ticket(models.Model):
    image = models.ImageField(default="avatar.svg", blank=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey('Subject', on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True, blank=True)
    contributors = models.ManyToManyField(User, related_name='contributors', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    dateNow = models.DateTimeField(auto_now=True)
    is_open = models.BooleanField(default=True)
    is_pending = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.subject.name
    

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Comment(models.Model):
    image = models.ImageField(default="avatar.svg", blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    body = models.TextField(max_length=150)
    contributors = models.ManyToManyField(User, related_name='comment_contributors', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]


# class Upvote(models.Model):
#     comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
#     count = models.IntegerField(default=0)
    
#     def __str__(self):
#         return self.count
    
    
# class Downvote(models.Model):
#     comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
#     count = models.IntegerField(default=0)
    
#     def __str__(self):
#         return self.count
    