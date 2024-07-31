from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('userprofile/', views.edit_userprofile, name='edit_userprofile'),
    path('companyprofile/', views.edit_companyprofile, name='edit_companyprofile'),
    # Add other URLs as needed
]