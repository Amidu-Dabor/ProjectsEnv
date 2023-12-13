from django.db import models
from email.policy import default
import datetime
from unicodedata import name
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy
from ckeditor.fields import RichTextField
from django.contrib.auth.backends import BaseBackend
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractUser, AbstractBaseUser, PermissionsMixin, Group, \
    Permission


# Create your models here.

# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self.create_user(email, password, **extra_fields)

class CustomAccountManager(BaseUserManager):

    def create_superuser(self, user_name, first_name, other_name, email, password, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', False)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff = True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be assigned to is_superuser = True.')

        return self.create_user(user_name, first_name, other_name, email, password, **extra_fields)

    def create_user(self, user_name, first_name, other_name, email, password, **extra_fields):

        if not email:
            raise ValueError(gettext_lazy('You must provide an email address.'))

        email = self.normalize_email(email)
        user = self.model(user_name=user_name, first_name=first_name, other_name=other_name, email=email,
                          **extra_fields)
        user.set_password(password)
        user.save()
        return user


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, default='None')

    def __str__(self):
        return self.name


# class CustomPermissionManager(PermissionManager):
#     pass


# class CustomPermission(PermissionsMixin):
#     objects = CustomPermissionManager()


#     class Meta:
#         verbose_name = 'Custom Permission'
#         verbose_name_plural = 'Custom Permissions'


# class CustomUserPermissions(Permission):
#     class Meta:
#         permissions = (
#             ('can_login_as_superuser', 'Can login as a superuser'),
#         )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    photo = models.ImageField(default="avatar.svg", null=True)
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_department')
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=70, null=False)
    user_name = models.CharField(max_length=50, unique=True, null=False)
    email = models.EmailField(gettext_lazy('email address'), unique=True)
    start_date = models.DateTimeField(default=timezone.now)
    biography = RichTextField(gettext_lazy('biography'), max_length=500, blank=True)
    is_student = models.BooleanField(default=False)
    uid = models.PositiveIntegerField(unique=True, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = CustomAccountManager()

    groups = models.ManyToManyField(
        Group,
        verbose_name=("groups"),
        blank=True,
        help_text=(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="customuser_set",
        related_query_name="customuser",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=("user permissions"),
        blank=True,
        help_text=("Specific permissions for this user."),
        related_name="customuser_set",
        related_query_name="customuser",
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'other_name']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    # def set_online(self):
    #     self.is_active = True
    #     self.last_login = timezone.now()
    #     self.save()

    # def set_offline(self):
    #     self.is_active = False
    #     self.save()

    # def is_user_online(self):
    #     threshold = timezone.now() - timezone.timedelta(minutes=5)
    #     return self.is_active and self.last_login > threshold


class Ticket(models.Model):
    # image = models.ImageField(default="avatar.svg", blank=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='ticket_creator')
    subject = models.ForeignKey('Subject', on_delete=models.SET_NULL, null=True, related_name='ticket_subject')
    description = models.TextField(null=True, blank=True)
    contributors = models.ManyToManyField(CustomUser, related_name='contributors', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)
    is_in_progress = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.subject.name


class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Comment(models.Model):
    # image = models.ImageField(default="avatar.svg", blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comment_user')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comment_ticket')
    body = models.TextField(max_length=150)
    contributors = models.ManyToManyField(CustomUser, related_name='comment_contributors', blank=True, )
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
