from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import Textarea
from django.utils.html import format_html

# Registering my models
from .models import CustomUser, Department, Ticket, Subject, Comment

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     pass

class UserAdmin(admin.ModelAdmin):
    search_fields = ('user_name', 'first_name', 'last_name', 'department', 'email')
    list_filter = ('is_staff', 'is_student', 'is_superuser', 'is_active', 'department')
    ordering = ('-start_date',)
    list_display = ('uid', 'user_name', 'profile_photo', 'first_name', 'last_name', 'department', 'is_staff', 'is_student', 'is_superuser', 'is_active')
    list_editable = ('is_staff', 'is_student', 'is_superuser', 'is_active', 'department')
    list_display_links = ('uid', 'user_name')
    fieldsets = (
        (None, {'fields': ('uid', 'photo', 'user_name', 'first_name', 'last_name', 'department', 'email', 'password')}),
        ('Personal', {'fields': ('biography',)}),
        ('Permission', {'fields': ('is_staff', 'is_student', 'is_superuser', 'is_active')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'user_name', 'department', 'email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active')
        }),
    )
    list_per_page = 20
    save_on_top = True

    def profile_photo(self, obj):
        return format_html(f'<img src="/images/{obj.photo}" style="height:30px;width:30px;border-radius:50%;">')


class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ('id', 'name')
    list_display = ('id', 'name')
    list_per_page = 20


class TicketAdmin(admin.ModelAdmin):
    search_fields = ('id', 'creator', 'subject')
    list_filter = ('is_open', 'is_in_progress', 'is_resolved', 'is_closed', 'updated', 'created')
    ordering = ('-created',)
    list_display = ('id', 'creator', 'subject', 'description', 'is_open', 'is_in_progress', 'is_resolved', 'is_closed')
    list_editable = ('is_open', 'is_in_progress', 'is_resolved', 'is_closed')
    list_per_page = 20
    save_on_top = True


class SubjectAdmin(admin.ModelAdmin):
    search_fields = ('id', 'name')
    list_display = ('id', 'name')
    list_per_page = 20


class CommentAdmin(admin.ModelAdmin):
    search_fields = ('id', 'user', 'ticket')
    list_filter = ('created', 'updated')
    ordering = ('-created',)
    list_display = ('id', 'user', 'ticket', 'body')
    list_per_page = 20
    save_on_top = True


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Comment, CommentAdmin)
# admin.site.register(Upvote)
# admin.site.register(Downvote)
