from django.urls import path
from . import views

urlpatterns = [
    path('admin/overview_link_assistent_apotheek_admin/<int:user_id>/', views.overview_link_assistent_apotheek_admin, name='overview_link_assistent_apotheek_admin'),
]
