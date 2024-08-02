from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('events/', views.events_json, name='events_json'),
    path('events/<int:event_id>/<str:action>/', views.update_event_status, name='update_event_status'),
]
