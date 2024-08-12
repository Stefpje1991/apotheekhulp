from django.urls import path
from . import views

urlpatterns = [
    path('admin/overview_link_assistent_apotheek_admin/<int:user_id>/', views.overview_link_assistent_apotheek_admin, name='overview_link_assistent_apotheek_admin'),
    path('overview_events_apotheek_and_admin/', views.overview_events_apotheek_and_admin, name='overview_events_apotheek_and_admin')
]
