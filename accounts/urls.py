from django.urls import path
from . import views

urlpatterns = [
    path('registerAssistent/', views.register_assistent, name='register_assistent'),
    # Add other URLs as needed
]