from django.contrib import admin

from invoice.models import LinkBetweenAssistentAndApotheek, InvoiceOverview

# Register your models here.
admin.site.register(LinkBetweenAssistentAndApotheek)
admin.site.register(InvoiceOverview)