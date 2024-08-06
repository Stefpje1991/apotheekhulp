from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('change_password/', views.change_password, name='change_password'),
    path('userprofile/', views.edit_userprofile, name='edit_userprofile'),
    path('edit_assistentprofile/<int:assistent_id>/', views.edit_assistentprofile, name='edit_assistentprofile'),
    path('companyprofile/', views.edit_companyprofile, name='edit_companyprofile'),
    path('overview_assistenten', views.overview_assistenten, name='overview_assistenten'),
    path('overview_apotheken', views.overview_apotheken, name='overview_apotheken'),
    # Add other URLs as needed
]