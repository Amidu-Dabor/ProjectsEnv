from django.contrib import admin
from django.forms import Textarea
from django.utils.html import format_html

# Registering my models
from .models import User, Department, Ticket, Subject, Comment

class UserAdmin(admin.ModelAdmin):
    search_fields = ('full_name', 'email', 'user_name', 'department')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('-start_date',)
    list_display = ('id', 'email', 'profile_photo', 'full_name', 'user_name', 'department', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('avatar', 'full_name', 'user_name' , 'department', 'email', 'password')}),
        ('Personal', {'fields': ('biography',)}),
        ('Permission', {'fields': ('is_staff', 'is_superuser', 'is_active')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name', 'user_name', 'department', 'email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active')
        }),
    )
    list_per_page = 15
    save_on_top = True


    def profile_photo(self, obj):
        return format_html(f'<img src="/images/{obj.avatar}" style="height:25px;width:25px;border-radius:50%;">')


class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ('id', 'name')
    list_display = ('id', 'name')
    list_per_page = 15


class TicketAdmin(admin.ModelAdmin):
    search_fields = ('id', 'creator', 'subject')
    list_filter = ('is_open', 'is_pending', 'is_approved', 'is_resolved', 'updated', 'created')
    ordering = ('-created',)
    list_display = ('id', 'creator', 'subject', 'description', 'is_open', 'is_pending', 'is_approved', 'is_resolved')
    list_per_page = 15
    save_on_top = True


class SubjectAdmin(admin.ModelAdmin):
    search_fields = ('id', 'name')
    list_display = ('id', 'name')
    list_per_page = 15


class CommentAdmin(admin.ModelAdmin):
    search_fields = ('id', 'user', 'ticket')
    list_filter = ('created', 'updated')
    ordering = ('-created',)
    list_display = ('id', 'image', 'user', 'ticket', 'body')
    list_per_page = 15
    save_on_top = True


admin.site.register(User, UserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Comment, CommentAdmin)
# admin.site.register(Upvote)
# admin.site.register(Downvote)
