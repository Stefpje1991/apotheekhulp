from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('change_password/', views.change_password, name='change_password'),
    path('userprofile/', views.edit_userprofile, name='edit_userprofile'),
    path('edit_companyprofile_assistent_admin/<int:assistent_id>/', views.edit_companyprofile_assistent_admin, name='edit_companyprofile_assistent_admin'),
    path('edit_companyprofile_apotheek_admin/<int:apotheek_id>/', views.edit_companyprofile_apotheek_admin, name='edit_companyprofile_apotheek_admin'),
    path('edit_userprofile_admin/<int:user_id>/', views.edit_userprofile_admin, name='edit_userprofile_admin'),
    path('change_password_user/<int:user_id>/', views.change_password_user, name='change_password_user'),
    path('companyprofile/', views.edit_companyprofile, name='edit_companyprofile'),
    path('overview_assistenten', views.overview_assistenten, name='overview_assistenten'),
    path('overview_apotheken', views.overview_apotheken, name='overview_apotheken'),
    path('register_assistent/', views.add_nieuwe_assistent_admin, name='add_nieuwe_assistent_admin'),
    path('register_apotheek/', views.add_nieuwe_apotheek_admin, name='add_nieuwe_apotheek_admin')
    # Add other URLs as needed
]