from unicodedata import name
from django.urls import path, include
from django.contrib.auth import views as auth_views
# from django.contrib.auth.urls
from . import views

urlpatterns = [
    # path('', views.dashboard_with_pivot, name='dashboard_with_pivot'),
    # path('data', views.pivot_data, name='pivot_data'),
    
    path('login/', views.login_page, name='login'),
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_page, name='register'),
    
    path('request/<str:pk>/', views.ticket, name='ticket'),
    path('profile/<str:pk>/', views.user_profile, name='user-profile'),

    #CRUD OPERATIONS
    # Requests
    path('make-request/', views.create_ticket, name='create-ticket'),
    path('update-request/<str:pk>/', views.update_ticket, name='update-ticket'),
    path('delete-request/<str:pk>/', views.delete_ticket, name='delete-ticket'),
    # Requests Comments
    path('delete-comment/<str:pk>/', views.delete_comment, name='delete-comment'),
    path('edit-comment/<str:pk>/', views.edit_comment, name='edit-comment'),

    # Users Accounts Management
    path('update-user/', views.update_user, name='update-user'),
    
    # Subjects List (Navbar-left)
    path('subjects/', views.subjects_page, name='subjects'),
    path('activities/', views.activity_page, name='activities'),
    
    # Requests Table
    path('requests-datatable/', views.request_page, name='requests-datatable-page'),
    path('requests-table/', views.requests_table, name='requests-table'),

    # Password Reset
    path('login/', 
        auth_views.LoginView.as_view(template_name='base/login_register.html'), name="login"),
    path('password_reset/', 
        auth_views.PasswordResetView.as_view(template_name='base/password_reset.html'), name="password_reset"),
    path('password_reset_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name='base/password_reset_sent.html'), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name='base/password_reset_form.html'), name="password_reset_confirm"),
    path('password_reset_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name='base/password_reset_complete.html'), name="password_reset_complete"),

    # path('accounts/', include('django.contrib.auth.urls')),
    # accounts/login/ [name='login']
    # accounts/logout/ [name='logout']
    # accounts/password_change/ [name='password_change']
    # accounts/password_change/done/ [name='password_change_done']
    # accounts/password_reset/ [name='password_reset']
    # accounts/password_reset/done/ [name='password_reset_done']
    # accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
    # accounts/reset/done/ [name='password_reset_complete']
]
