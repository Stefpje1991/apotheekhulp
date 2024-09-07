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
    path('edit_link/<int:user_id>/<int:link_id>/', views.edit_link_between_assistent_and_apotheek, name='edit_link_between_assistent_and_apotheek'),
    path('admin/edit_event_overview_pagina_goed_te_keuren_door_assistent_admin/<int:event_id>/', views.edit_event_overview_pagina_goed_te_keuren_door_assistent_admin, name='edit_event_overview_pagina_goed_te_keuren_door_assistent_admin'),
    path('admin/accept_apotheek_event/<int:event_id>/', views.accept_apotheek_event, name='accept_apotheek_event'),
    path('create_invoice/', views.create_invoice, name='create_invoice'),
    path('admin/create_invoice_apotheek/', views.create_invoice_apotheek_admin, name='create_invoice_apotheek_admin'),
    path('admin/overview_facturen_assistent/<int:user_id>/', views.overview_facturen_assistent_admin, name='overview_facturen_assistent_admin'),
    path('admin/overview_facturen_apotheek/<int:user_id>', views.overview_facturen_apotheek_admin, name='overview_facturen_apotheek_admin'),
    path('admin/toggle_invoice_status_factuur_assistent/', views.toggle_invoice_status_factuur_assistent, name='toggle_invoice_status_factuur_assistent'),
    path('admin/toggle_invoice_status_factuur_apotheek/', views.toggle_invoice_status_factuur_apotheek, name='toggle_invoice_status_factuur_apotheek'),
    path('admin/create_link_between_assistent_and_apotheek/', views.create_link_between_assistent_and_apotheek, name='create_link_between_assistent_and_apotheek'),
    path('admin/overview_all_invoices_assistenten_admin/', views.overview_all_invoices_assistenten_admin, name='overview_all_invoices_assistenten_admin'),
    path('admin/overview_all_invoices_apotheken_admin/', views.overview_all_invoices_apotheken_admin, name='overview_all_invoices_apotheken_admin'),
    path('admin/get_filtered_invoices/', views.get_filtered_invoices, name='get_filtered_invoices'),
]
