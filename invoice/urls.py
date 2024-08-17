from django.urls import path
from . import views

urlpatterns = [
    path('admin/overview_link_assistent_apotheek_admin/<int:user_id>/', views.overview_link_assistent_apotheek_admin, name='overview_link_assistent_apotheek_admin'),
    path('admin/overview_events_admin/<int:user_id>/', views.overview_events_admin, name='overview_events_admin'),
    path('admin/overview_events_admin/', views.overview_all_events_admin, name='overview_all_events_admin'),
    path('overview_events_apotheek/', views.overview_events_apotheek, name='overview_events_apotheek'),
    path('overview_events_assistent/', views.overview_events_assistent, name='overview_events_assistent'),
    path('update_event_status/<int:event_id>/', views.update_event_status, name='update_event_status'),
    path('update_event_status_assistent/<int:event_id>/', views.update_event_status_assistent, name='update_event_status_assistent'),
    path('delete-link/<int:user_id>/<int:link_id>/', views.delete_link, name='delete_link'),
    path('admin/get_event_data/<int:event_id>/', views.get_event_data, name='get_event_data'),
    path('admin/edit_event_overview_pagina_goed_te_keuren_door_assistent_admin/<int:event_id>/', views.edit_event_overview_pagina_goed_te_keuren_door_assistent_admin, name='edit_event_overview_pagina_goed_te_keuren_door_assistent_admin'),
    path('admin/accept_apotheek_event/<int:event_id>/', views.accept_apotheek_event, name='accept_apotheek_event'),
]
