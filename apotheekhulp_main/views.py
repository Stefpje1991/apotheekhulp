from django.db.models import Q, Sum, F
from django.shortcuts import render
from django.http import HttpResponse

from calendar_app.models import Event
from invoice.models import InvoiceOverview, InvoiceApotheekOverview


def home(request):
    declined_count = Event.objects.filter(
        Q(status='Declined') | Q(status_apotheek='Declined')
    ).count()

    geweigerde_events_door_assistenten = Event.objects.filter(status='Declined').count()
    geweigerde_events_door_apotheken = Event.objects.filter(status_apotheek='Declined').count()
    unpaid_invoices_by_assistenten_sum = InvoiceOverview.objects.filter(invoice_paid=False).aggregate(
        total=Sum(F('invoice_amount') + F('invoice_btw'))
    )['total'] or 0  # Default to 0.0 if there are no unpaid invoices
    unpaid_invoices_by_apotheken_sum = InvoiceApotheekOverview.objects.filter(invoice_paid=False).aggregate(
        total=Sum(F('invoice_amount') + F('invoice_btw'))
    )['total'] or 0  # Default to 0.0 if there are no unpaid invoices
    unpaid_invoices_by_assistenten_sum = round(unpaid_invoices_by_assistenten_sum, 2)
    unpaid_invoices_by_apotheken_sum = round(unpaid_invoices_by_apotheken_sum, 2)

    # Determine if any declined events exist
    has_declined_events_of_assistenten = geweigerde_events_door_assistenten > 0
    has_declined_events_of_apotheken = geweigerde_events_door_apotheken > 0

    context = {
        'declined_count': declined_count,
        'geweigerde_events_door_assistenten': geweigerde_events_door_assistenten,
        'geweigerde_events_door_apotheken': geweigerde_events_door_apotheken,
        'has_declined_events_of_assistenten': has_declined_events_of_assistenten,
        'has_declined_events_of_apotheken': has_declined_events_of_apotheken,
        'unpaid_invoices_by_assistenten_sum': unpaid_invoices_by_assistenten_sum,
        'unpaid_invoices_by_apotheken_sum': unpaid_invoices_by_apotheken_sum,
    }
    return render(request, 'index.html', context)
