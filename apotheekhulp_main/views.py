from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F
from django.shortcuts import render, redirect
from django.http import HttpResponse

from calendar_app.models import Event
from invoice.models import InvoiceOverview, InvoiceApotheekOverview


@login_required(login_url='login')
def home(request):
    if request.user.role == 3:
        return redirect('overview_all_events_admin')
    elif request.user.role == 2:
        return redirect('overview_events_apotheek')
    else:
        return redirect('overview_events_assistent')

