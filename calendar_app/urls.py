from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('events/<int:event_id>/<str:action>/', views.update_event_status, name='update_event_status'),
    path('assistents/', views.fetch_assistents, name='fetch_assistents'),
    path('apotheken/', views.fetch_apotheken, name='fetch_apotheken'),
    path('events/add/', views.add_event, name='add_event'),
    path('delete_event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('edit_event/<int:event_id>/edit/', views.edit_event, name='edit_event'),        # URL for edit
    path('events/', views.events_json, name='events_json'),
]
