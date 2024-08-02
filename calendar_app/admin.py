# admin.py
from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
    'start_time', 'end_time', 'category', 'assistent', 'apotheek', 'created_by', 'status', 'created_date',
    'modified_date')
    search_fields = ('start_time', 'assistent', 'apotheek')
    list_filter = ('start_time', 'end_time', 'category', 'status', 'assistent', 'apotheek', 'created_by')
    ordering = ('-created_date',)
