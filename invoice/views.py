import json
from datetime import datetime
from datetime import timedelta
from io import BytesIO  # For handling in-memory file objects

import pytz
import sweetify
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Sum, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import get_template  # For loading and rendering HTML templates
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from xhtml2pdf import pisa  # For converting HTML to PDF

from accounts.decorators import role_required
from accounts.models import Assistent, User, Apotheek
from calendar_app.models import Event
from .models import InvoiceOverview, InvoiceDetail, InvoiceApotheekOverview, InvoiceApotheekDetail
from .models import LinkBetweenAssistentAndApotheek


# Create your views here.
@role_required(3)
@login_required(login_url='login')
def overview_link_assistent_apotheek_admin(request, user_id):
    gebruiker = get_object_or_404(User, id=user_id)
    assistent_id = 0
    apotheek_id = 0
    links = []
    assistent = None
    apotheek = None

    # Get assistent and apotheek based on role
    if gebruiker.role == 1:
        assistent = get_object_or_404(Assistent, user=gebruiker)
        assistent_id = assistent.id
        links = LinkBetweenAssistentAndApotheek.objects.filter(assistent=assistent)
    elif gebruiker.role == 2:
        apotheek = get_object_or_404(Apotheek, user=gebruiker)
        apotheek_id = apotheek.id
        links = LinkBetweenAssistentAndApotheek.objects.filter(apotheek=apotheek)

    # Fetch available assistents and apotheken
    all_assistents = Assistent.objects.all()
    all_apotheken = Apotheek.objects.all()

    context = {
        'user_id': user_id,
        'gebruiker': gebruiker,
        'assistent_id': assistent_id,
        'apotheek_id': apotheek_id,
        'links': links,
        'assistent': assistent,
        'apotheek': apotheek,
        'all_assistents': all_assistents,
        'all_apotheken': all_apotheken,
    }

    return render(request, 'invoice/admin/overview_link_assistent_apotheek_admin.html', context)


@role_required(2, 3)
@login_required(login_url='login')
def overview_events_apotheek(request):
    user_id = request.user.id
    apotheek = get_object_or_404(Apotheek, user=request.user)
    te_bekijken_events_door_apotheek = Event.objects.filter(apotheek=apotheek, status='Accepted',
                                                            status_apotheek='noaction')
    historische_events_per_apotheek = Event.objects.filter(apotheek=apotheek, status='Accepted').exclude(
        status_apotheek='noaction')
    apotheek_id = apotheek.id
    links = LinkBetweenAssistentAndApotheek.objects.filter(apotheek=apotheek)
    context = {
        'user_id': user_id,
        'events_to_be_reviewed_by_apotheek': te_bekijken_events_door_apotheek,
        'apotheek': apotheek,
        'apotheek_id': apotheek_id,
        'links': links,
        'historische_events_per_apotheek': historische_events_per_apotheek
    }
    return render(request, 'invoice/overview_events_apotheek.html', context)


@role_required(2, 3)
def update_event_status(request, event_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse the JSON data
            status_apotheek = data.get('status_apotheek')

            # Process the data (e.g., update the event status)
            event = Event.objects.get(id=event_id)
            event.status_apotheek = status_apotheek
            event.status_apotheek_changed_by = request.user
            event.save()

            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Event not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


@role_required(1, 3)
def update_event_status_assistent(request, event_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse the JSON data
            status = data.get('status')

            # Process the data (e.g., update the event status)
            event = Event.objects.get(id=event_id)
            event.status = status
            event.save()

            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Event not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


@role_required(1, 3)
@login_required(login_url='login')
def overview_events_assistent(request):
    assistent = get_object_or_404(Assistent, user=request.user)
    te_bekijken_events_door_assistent = Event.objects.filter(assistent=assistent, status='noaction')
    te_bekijken_events_door_apotheek = Event.objects.filter(assistent=assistent, status='Accepted').exclude(
        status_apotheek='Accepted')
    nog_te_factureren_events_door_assistent = Event.objects.filter(assistent=assistent, invoiced=False,
                                                                   status='Accepted',
                                                                   status_apotheek='Accepted')
    facturen_van_assistent = InvoiceOverview.objects.filter(invoice_created_by=assistent)

    items_nog_te_factureren_door_assistent = []
    for item in nog_te_factureren_events_door_assistent:
        id = item.id
        start_time = item.start_time
        end_time = item.end_time
        aanwezige_tijd = end_time - start_time
        pauzeduur = timedelta(minutes=item.pauzeduur)
        gewerkte_uren = (end_time - start_time - pauzeduur).total_seconds() / 3600
        gewerkte_uren_modal = end_time - start_time - pauzeduur
        gewerkte_uren = round(gewerkte_uren, 4)
        assistent = item.assistent
        apotheek = item.apotheek
        try:
            link = LinkBetweenAssistentAndApotheek.objects.get(assistent=assistent, apotheek=apotheek)
            uurtariefAssistent = float(link.uurtariefAssistent)
            afstandInKilometers = link.afstandInKilometers
            uurtariefApotheek = float(link.uurtariefApotheek)
            kilometervergoeding = link.kilometervergoeding
            bedragFietsvergoeding = 0.00
            if kilometervergoeding:
                bedragFietsvergoeding = round(afstandInKilometers * 0.43, 2)
            totaalbedragZonderFietsvergoeding = round(gewerkte_uren * uurtariefAssistent, 2)
            totaalbedragWerk = round(round(gewerkte_uren * uurtariefAssistent, 2) + bedragFietsvergoeding, 2)
        except:
            link = ""
            uurtariefAssistent = 0
            uurtariefApotheek = 0
            kilometervergoeding = False
            afstandInKilometers = 0
            totaalbedragWerk = 0
            bedragFietsvergoeding = 0.00
            totaalbedragZonderFietsvergoeding = 0.00

        item_to_add = {
            'id': id,
            'start_time': start_time,
            'end_time': end_time,
            'pauzeduur': pauzeduur,
            'assistent': assistent,
            'apotheek': apotheek,
            'link': link,
            'uurtariefAssistent': uurtariefAssistent,
            'uurtariefApotheek': uurtariefApotheek,
            'afstandinKilometers': afstandInKilometers,
            'kilometervergoeding': kilometervergoeding,
            'totaalbedragWerk': totaalbedragWerk,
            'bedragFietsvergoeding': bedragFietsvergoeding,
            'aanwezige_tijd': aanwezige_tijd,
            'gewerkte_tijd': gewerkte_uren_modal,
            'totaalbedrag_zonder_fietsvergoeding': totaalbedragZonderFietsvergoeding
        }

        items_nog_te_factureren_door_assistent.append(item_to_add)
    context = {
        'te_bekijken_events_door_assistent': te_bekijken_events_door_assistent,
        'nog_te_factureren_events': items_nog_te_factureren_door_assistent,
        'te_bekijken_events_door_apotheek': te_bekijken_events_door_apotheek,
        'facturen_van_assistent': facturen_van_assistent
    }
    return render(request, 'invoice/overview_events_assistent.html', context)


@role_required(3)
def delete_link(request, user_id, link_id):
    link = get_object_or_404(LinkBetweenAssistentAndApotheek, id=link_id)

    if request.method == 'POST':
        # Ensure that the current user has permission to delete the link
        link.actief = False
        link.save()
        messages.success(request, 'De link is succesvol gedeactiveerd.')

    return redirect('overview_link_assistent_apotheek_admin', user_id=user_id)


@role_required(3)
def overview_events_admin(request, user_id):
    gebruiker = get_object_or_404(User, id=user_id)
    assistent_id = 0
    apotheek_id = 0
    assistent = None
    apotheek = None
    events_status_no_action = None
    nog_te_factureren_dagen_aan_apotheek = None
    gewerkte_dagen_te_accepteren_door_apotheek = None
    gefactureerde_dagen_aan_apotheek = None
    betaalde_dagen_door_apotheek = None
    event_status_declined_by_assistent = None
    items_nog_te_factureren_door_assistent = []
    items_nog_te_factureren_aan_apotheek = []

    # Helper function to calculate invoice items
    def calculate_invoice_item(item, uurtarief, is_apotheek=False):
        start_time = item.start_time
        end_time = item.end_time
        aanwezige_tijd = end_time - start_time
        pauzeduur = timedelta(minutes=item.pauzeduur)
        gewerkte_uren = (end_time - start_time - pauzeduur).total_seconds() / 3600
        gewerkte_uren_modal = end_time - start_time - pauzeduur
        gewerkte_uren = round(gewerkte_uren, 4)

        try:
            link = LinkBetweenAssistentAndApotheek.objects.get(assistent=item.assistent, apotheek=item.apotheek)
            afstandInKilometers = link.afstandInKilometers
            kilometervergoeding = link.kilometervergoeding
            bedragFietsvergoeding = round(afstandInKilometers * 0.43, 2) if kilometervergoeding else 0.00
            totaalbedragZonderFietsvergoeding = round(gewerkte_uren * float(uurtarief), 2)
            totaalbedragWerk = round(totaalbedragZonderFietsvergoeding + bedragFietsvergoeding, 2)
        except:
            link, afstandInKilometers, kilometervergoeding = "", 0, False
            totaalbedragWerk, bedragFietsvergoeding, totaalbedragZonderFietsvergoeding = 0, 0.00, 0.00

        return {
            'id': item.id,
            'start_time': start_time,
            'end_time': end_time,
            'pauzeduur': pauzeduur,
            'assistent': item.assistent,
            'apotheek': item.apotheek,
            'link': link,
            'uurtarief': uurtarief,
            'afstandinKilometers': afstandInKilometers,
            'kilometervergoeding': kilometervergoeding,
            'totaalbedragWerk': totaalbedragWerk,
            'bedragFietsvergoeding': bedragFietsvergoeding,
            'aanwezige_tijd': aanwezige_tijd,
            'gewerkte_tijd': gewerkte_uren_modal,
            'totaalbedrag_zonder_fietsvergoeding': totaalbedragZonderFietsvergoeding
        }

    # Determine role and get the appropriate instance
    if gebruiker.role == 1:  # Assistent
        assistent = get_object_or_404(Assistent, user=gebruiker)
        assistent_id = assistent.id

        # Fetch relevant events
        events_status_no_action = Event.objects.filter(assistent=assistent, status='noaction').order_by('start_time')
        event_status_declined_by_assistent = Event.objects.filter(assistent=assistent, status='Declined').order_by(
            'start_time')
        gewerkte_dagen_te_accepteren_door_apotheek = Event.objects.filter(assistent=assistent,
                                                                          status='Accepted').exclude(
            status_apotheek='Accepted').order_by('start_time')
        nog_te_factureren_dagen = Event.objects.filter(assistent=assistent, status='Accepted',
                                                       status_apotheek='Accepted', invoiced=False).order_by(
            'start_time')
        nog_te_factureren_dagen_aan_apotheek = Event.objects.filter(assistent=assistent, status='Accepted',
                                                                    status_apotheek='Accepted', invoiced=True,
                                                                    invoiced_to_apotheek=False).order_by('start_time')
        gefactureerde_dagen_aan_apotheek = Event.objects.filter(assistent=assistent, status='Accepted',
                                                                status_apotheek='Accepted', invoiced=True,
                                                                invoiced_to_apotheek=True,
                                                                paid_by_apotheek=False).order_by('start_time')
        betaalde_dagen_door_apotheek = Event.objects.filter(assistent=assistent, status='Accepted',
                                                            status_apotheek='Accepted', invoiced=True,
                                                            invoiced_to_apotheek=True, paid_by_apotheek=True).order_by(
            'start_time')

        # Populate items_nog_te_factureren_door_assistent
        for item in nog_te_factureren_dagen:
            try:
                uurtariefAssistent = LinkBetweenAssistentAndApotheek.objects.get(assistent=assistent,
                                                                                 apotheek=item.apotheek).uurtariefAssistent
            except:
                uurtariefAssistent = 0
            item_to_add = calculate_invoice_item(item, uurtariefAssistent)
            items_nog_te_factureren_door_assistent.append(item_to_add)

        # Populate items_nog_te_factureren_aan_apotheek
        for item in nog_te_factureren_dagen_aan_apotheek:
            try:
                uurtariefApotheek = LinkBetweenAssistentAndApotheek.objects.get(assistent=assistent,
                                                                                apotheek=item.apotheek).uurtariefApotheek
            except:
                uurtariefApotheek = 0
            item_to_add = calculate_invoice_item(item, uurtariefApotheek, is_apotheek=True)
            items_nog_te_factureren_aan_apotheek.append(item_to_add)

    elif gebruiker.role == 2:  # Apotheek
        apotheek = get_object_or_404(Apotheek, user=gebruiker)
        apotheek_id = apotheek.id

        # Fetch relevant events
        events_status_no_action = Event.objects.filter(apotheek=apotheek, status='noaction').order_by('start_time')
        event_status_declined_by_assistent = Event.objects.filter(apotheek=apotheek, status='Declined').order_by(
            'start_time')
        gewerkte_dagen_te_accepteren_door_apotheek = Event.objects.filter(apotheek=apotheek, status='Accepted').exclude(
            status_apotheek='Accepted').order_by('start_time')
        nog_te_factureren_dagen = Event.objects.filter(apotheek=apotheek, status='Accepted', status_apotheek='Accepted',
                                                       invoiced=False).order_by('start_time')
        nog_te_factureren_dagen_aan_apotheek = Event.objects.filter(apotheek=apotheek, status='Accepted',
                                                                    status_apotheek='Accepted', invoiced=True,
                                                                    invoiced_to_apotheek=False).order_by('start_time')
        gefactureerde_dagen_aan_apotheek = Event.objects.filter(apotheek=apotheek, status='Accepted',
                                                                status_apotheek='Accepted', invoiced=True,
                                                                invoiced_to_apotheek=True,
                                                                paid_by_apotheek=False).order_by('start_time')
        betaalde_dagen_door_apotheek = Event.objects.filter(apotheek=apotheek, status='Accepted',
                                                            status_apotheek='Accepted', invoiced=True,
                                                            invoiced_to_apotheek=True, paid_by_apotheek=True).order_by(
            'start_time')

        # Populate items_nog_te_factureren_door_assistent
        for item in nog_te_factureren_dagen:
            try:
                uurtariefAssistent = LinkBetweenAssistentAndApotheek.objects.get(assistent=item.assistent,
                                                                                 apotheek=apotheek).uurtariefAssistent
            except:
                uurtariefAssistent = 0
            item_to_add = calculate_invoice_item(item, uurtariefAssistent)
            items_nog_te_factureren_door_assistent.append(item_to_add)

        # Populate items_nog_te_factureren_aan_apotheek
        for item in nog_te_factureren_dagen_aan_apotheek:
            try:
                uurtariefApotheek = LinkBetweenAssistentAndApotheek.objects.get(assistent=item.assistent,
                                                                                apotheek=apotheek).uurtariefApotheek
            except:
                uurtariefApotheek = 0
            item_to_add = calculate_invoice_item(item, uurtariefApotheek, is_apotheek=True)
            items_nog_te_factureren_aan_apotheek.append(item_to_add)
    # Prepare context
    context = {
        'user_id': user_id,
        'gebruiker': gebruiker,
        'assistent_id': assistent_id,
        'apotheek_id': apotheek_id,
        'assistent': assistent,  # Pass the Assistent object
        'apotheek': apotheek,  # Pass the Apotheek object
        'events_status_no_action': events_status_no_action,
        'event_status_declined_by_assistent': event_status_declined_by_assistent,
        'gewerkte_dagen_te_accepteren_door_apotheek': gewerkte_dagen_te_accepteren_door_apotheek,
        'nog_te_factureren_dagen_aan_apotheek': nog_te_factureren_dagen_aan_apotheek,
        'items_nog_te_factureren_door_assistent': items_nog_te_factureren_door_assistent,
        'items_nog_te_factureren_aan_apotheek': items_nog_te_factureren_aan_apotheek,
        'betaalde_dagen_door_apotheek': betaalde_dagen_door_apotheek,
        'gefactureerde_dagen_aan_apotheek': gefactureerde_dagen_aan_apotheek
    }

    return render(request, 'invoice/admin/overview_events_per_gebruiker.html', context)


@role_required(3)
def overview_all_events_admin(request):
    goed_te_keuren_events_door_assistent = Event.objects.filter(status='noaction').order_by('start_time')
    geweigerde_events_door_assistenten = Event.objects.filter(status='Declined').order_by('start_time')
    goed_te_keuren_events_door_apotheek = Event.objects.filter(status='Accepted', status_apotheek='noaction').order_by(
        'start_time')
    geweigerde_events_door_apotheken = Event.objects.filter(status='Accepted', status_apotheek='Declined').order_by(
        'start_time')
    nog_te_factureren_door_assistent = Event.objects.filter(status='Accepted', status_apotheek='Accepted',
                                                            invoiced=False).order_by('start_time')
    nog_te_factureren_aan_apotheek = (Event.objects.filter(status='Accepted', status_apotheek='Accepted',
                                                           invoiced=True, invoiced_to_apotheek=False)
                                      .order_by('start_time'))
    nog_te_betalen_door_apotheek = Event.objects.filter(status='Accepted', status_apotheek='Accepted',
                                                        invoiced=True, invoiced_to_apotheek=True,
                                                        paid_by_apotheek=False).order_by('start_time')
    betaalde_events_door_apotheek = Event.objects.filter(status='Accepted', status_apotheek='Accepted',
                                                         invoiced=True, invoiced_to_apotheek=True,
                                                         paid_by_apotheek=True).order_by('start_time')

    items_nog_te_factureren_door_assistent = []
    for item in nog_te_factureren_door_assistent:
        id = item.id
        start_time = item.start_time
        end_time = item.end_time
        aanwezige_tijd = end_time - start_time
        pauzeduur = timedelta(minutes=item.pauzeduur)
        gewerkte_uren = (end_time - start_time - pauzeduur).total_seconds() / 3600
        gewerkte_uren_modal = end_time - start_time - pauzeduur
        gewerkte_uren = round(gewerkte_uren, 4)
        assistent = item.assistent
        apotheek = item.apotheek
        try:
            link = LinkBetweenAssistentAndApotheek.objects.get(assistent=assistent, apotheek=apotheek)
            uurtariefAssistent = float(link.uurtariefAssistent)
            afstandInKilometers = link.afstandInKilometers
            uurtariefApotheek = link.uurtariefApotheek
            kilometervergoeding = link.kilometervergoeding
            bedragFietsvergoeding = 0.00
            if kilometervergoeding:
                bedragFietsvergoeding = round(afstandInKilometers * 0.43, 2)
            totaalbedragZonderFietsvergoeding = round(gewerkte_uren * uurtariefAssistent, 2)
            totaalbedragWerk = round(round(gewerkte_uren * uurtariefAssistent, 2) + bedragFietsvergoeding, 2)
        except:
            link = ""
            uurtariefAssistent = 0
            uurtariefApotheek = 0
            kilometervergoeding = False
            afstandInKilometers = 0
            totaalbedragWerk = 0
            bedragFietsvergoeding = 0.00
            totaalbedragZonderFietsvergoeding = 0.00

        item_to_add = {
            'id': id,
            'start_time': start_time,
            'end_time': end_time,
            'pauzeduur': pauzeduur,
            'assistent': assistent,
            'apotheek': apotheek,
            'link': link,
            'uurtariefAssistent': uurtariefAssistent,
            'uurtariefApotheek': uurtariefApotheek,
            'afstandinKilometers': afstandInKilometers,
            'kilometervergoeding': kilometervergoeding,
            'totaalbedragWerk': totaalbedragWerk,
            'bedragFietsvergoeding': bedragFietsvergoeding,
            'aanwezige_tijd': aanwezige_tijd,
            'gewerkte_tijd': gewerkte_uren_modal,
            'totaalbedrag_zonder_fietsvergoeding': totaalbedragZonderFietsvergoeding
        }

        items_nog_te_factureren_door_assistent.append(item_to_add)

    items_nog_te_factureren_aan_apotheek = []
    for item in nog_te_factureren_aan_apotheek:
        id = item.id
        start_time = item.start_time
        end_time = item.end_time
        aanwezige_tijd = end_time - start_time
        pauzeduur = timedelta(minutes=item.pauzeduur)
        gewerkte_uren = (end_time - start_time - pauzeduur).total_seconds() / 3600
        gewerkte_uren_modal = end_time - start_time - pauzeduur
        gewerkte_uren = round(gewerkte_uren, 4)
        assistent = item.assistent
        apotheek = item.apotheek
        try:
            link = LinkBetweenAssistentAndApotheek.objects.get(assistent=assistent, apotheek=apotheek)
            afstandInKilometers = link.afstandInKilometers
            uurtariefApotheek = link.uurtariefApotheek
            kilometervergoeding = link.kilometervergoeding
            bedragFietsvergoeding = 0.00
            if kilometervergoeding:
                bedragFietsvergoeding = round(afstandInKilometers * 0.43, 2)

            totaalbedragZonderFietsvergoeding = round(gewerkte_uren * float(uurtariefApotheek), 2)
            totaalbedragWerk = round(round(gewerkte_uren * float(uurtariefApotheek), 2) + bedragFietsvergoeding, 2)
        except:
            link = ""
            uurtariefApotheek = 0
            kilometervergoeding = False
            afstandInKilometers = 0
            totaalbedragWerk = 0
            bedragFietsvergoeding = 0.00
            totaalbedragZonderFietsvergoeding = 0.00

        item_to_add = {
            'id': id,
            'start_time': start_time,
            'end_time': end_time,
            'pauzeduur': pauzeduur,
            'assistent': assistent,
            'apotheek': apotheek,
            'link': link,
            'uurtariefApotheek': uurtariefApotheek,
            'afstandinKilometers': afstandInKilometers,
            'kilometervergoeding': kilometervergoeding,
            'totaalbedragWerk': totaalbedragWerk,
            'bedragFietsvergoeding': bedragFietsvergoeding,
            'aanwezige_tijd': aanwezige_tijd,
            'gewerkte_tijd': gewerkte_uren_modal,
            'totaalbedrag_zonder_fietsvergoeding': totaalbedragZonderFietsvergoeding
        }

        items_nog_te_factureren_aan_apotheek.append(item_to_add)

    paginator_goed_te_keuren_events_door_assistent = Paginator(goed_te_keuren_events_door_assistent, 5)
    page_number_goed_te_keuren_door_assistent = request.GET.get('page_goed_te_keuren_door_assistent')
    paginator_goed_te_keuren_events_door_assistent_obj = paginator_goed_te_keuren_events_door_assistent.get_page(
        page_number_goed_te_keuren_door_assistent)

    paginator_geweigerde_events_door_assistenten = Paginator(geweigerde_events_door_assistenten, 5)
    page_number_geweigerde_events_door_assistenten = request.GET.get('page_geweigerde_events_door_assistenten')
    paginator_geweigerde_events_door_assistenten_obj = paginator_geweigerde_events_door_assistenten.get_page(
        page_number_geweigerde_events_door_assistenten)

    paginator_goed_te_keuren_events_door_apotheek = Paginator(goed_te_keuren_events_door_apotheek, 5)
    page_number_goed_te_keuren_events_door_apotheek = request.GET.get('page_goed_te_keuren_events_door_apotheek')
    paginator_goed_te_keuren_events_door_apotheek_obj = paginator_goed_te_keuren_events_door_apotheek.get_page(
        page_number_goed_te_keuren_events_door_apotheek)

    paginator_geweigerde_events_door_apotheken = Paginator(geweigerde_events_door_apotheken, 5)
    page_number_geweigerde_events_door_apotheken = request.GET.get('page_geweigerde_events_door_apotheken')
    paginator_geweigerde_events_door_apotheken_obj = paginator_geweigerde_events_door_apotheken.get_page(
        page_number_geweigerde_events_door_apotheken)

    paginator_nog_te_factureren_door_assistent = Paginator(items_nog_te_factureren_door_assistent, 5)
    page_number_nog_te_factureren_door_assistent = request.GET.get('page_nog_te_factureren_door_assistent')
    paginator_nog_te_factureren_door_assistent_obj = paginator_nog_te_factureren_door_assistent.get_page(
        page_number_nog_te_factureren_door_assistent)

    paginator_nog_te_factureren_aan_apotheek = Paginator(items_nog_te_factureren_aan_apotheek, 5)
    page_number_nog_te_factureren_aan_apotheek = request.GET.get('page_nog_te_factureren_aan_apotheek')
    paginator_nog_te_factureren_aan_apotheek_obj = paginator_nog_te_factureren_aan_apotheek.get_page(
        page_number_nog_te_factureren_aan_apotheek)

    paginator_nog_te_betalen_door_apotheek = Paginator(nog_te_betalen_door_apotheek, 5)
    page_number_nog_te_betalen_door_apotheek = request.GET.get('page_nog_te_betalen_door_apotheek')
    paginator_nog_te_betalen_door_apotheek_obj = paginator_nog_te_betalen_door_apotheek.get_page(
        page_number_nog_te_betalen_door_apotheek)

    paginator_betaalde_events_door_apotheek = Paginator(betaalde_events_door_apotheek, 5)
    page_number_betaalde_events_door_apotheek = request.GET.get('page_betaalde_events_door_apotheek')
    paginator_betaalde_events_door_apotheek_obj = paginator_betaalde_events_door_apotheek.get_page(
        page_number_betaalde_events_door_apotheek)

    context = {
        'paginator_goed_te_keuren_events_door_assistent_obj': paginator_goed_te_keuren_events_door_assistent_obj,
        'paginator_geweigerde_events_door_assistenten_obj': paginator_geweigerde_events_door_assistenten_obj,
        'paginator_goed_te_keuren_events_door_apotheek_obj': paginator_goed_te_keuren_events_door_apotheek_obj,
        'paginator_geweigerde_events_door_apotheken_obj': paginator_geweigerde_events_door_apotheken_obj,
        'paginator_nog_te_factureren_door_assistent_obj': paginator_nog_te_factureren_door_assistent_obj,
        'paginator_nog_te_factureren_aan_apotheek_obj': paginator_nog_te_factureren_aan_apotheek_obj,
        'paginator_nog_te_betalen_door_apotheek_obj': paginator_nog_te_betalen_door_apotheek_obj,
        'paginator_betaalde_events_door_apotheek_obj': paginator_betaalde_events_door_apotheek_obj
    }
    return render(request, 'invoice/admin/overview_all_events.html', context=context)


@role_required(3)
def get_event_data(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
        assistenten = Assistent.objects.all()  # or use a queryset as needed
        apotheken = Apotheek.objects.all()  # or use a queryset as needed
    except Event.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Event not found'}, status=404)

    # Convert times from UTC to Brussels time
    local_tz = pytz.timezone('Europe/Brussels')

    event_start_time = event.start_time.astimezone(local_tz)
    event_end_time = event.end_time.astimezone(local_tz)

    event_data = {
        'id': event.id,
        'date': event_start_time.strftime('%Y-%m-%d'),
        'startTime': event_start_time.strftime('%H:%M'),
        'endTime': event_end_time.strftime('%H:%M'),
        'pauzeDuur': event.pauzeduur,
        'assistent': event.assistent.id,
        'apotheek': event.apotheek.id
    }

    assistent_data = [{'id': a.id, 'name': f"{a.user.first_name} {a.user.last_name}"} for a in assistenten]
    apotheek_data = [{'id': p.id, 'name': p.apotheek_naamBedrijf} for p in apotheken]

    return JsonResponse({
        'status': 'success',
        'event': event_data,
        'assistants': assistent_data,
        'pharmacies': apotheek_data
    })


@role_required(3)
@csrf_exempt
def edit_event_overview_pagina_goed_te_keuren_door_assistent_admin(request, event_id):
    if request.method == 'POST':
        try:
            event = get_object_or_404(Event, id=event_id)

            # Parse the JSON data from the request body
            import json
            data = json.loads(request.body)

            # Update event fields with new data
            event.date = data.get('date')
            event.start_time = f"{data.get('date')} {data.get('startTime')}"
            event.end_time = f"{data.get('date')} {data.get('endTime')}"
            event.pauzeduur = data.get('pauzeDuur')
            event.assistent_id = data.get('assistent')
            event.apotheek_id = data.get('apotheek')
            event.status = 'noaction'
            event.status_apotheek = 'noaction'
            event.status_apotheek_changed_by = None

            # Save the updated event to the database
            event.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})

    return JsonResponse({'status': 'error', 'error': 'Invalid request method'})


@role_required(3)
@csrf_exempt
def accept_apotheek_event(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        event.status = 'Accepted'
        event.status_apotheek = 'Accepted'
        event.status_apotheek_changed_by = request.user
        event.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})


@role_required(3)
def edit_link_between_assistent_and_apotheek(request, user_id, link_id):
    if request.method == 'POST':
        try:
            # Retrieve the link object
            link = get_object_or_404(LinkBetweenAssistentAndApotheek, id=link_id)

            # Parse the JSON data from the request body
            data = json.loads(request.body)

            # Update the link object with new values
            link.uurtariefAssistent = data.get('uurtariefAssistent', link.uurtariefAssistent)
            link.uurtariefApotheek = data.get('uurtariefApotheek', link.uurtariefApotheek)
            link.afstandInKilometers = data.get('afstandInKilometers', link.afstandInKilometers)
            link.kilometervergoeding = data.get('kilometervergoeding') == 'on'

            # Save the updated object
            link.save()

            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'error': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})

    return JsonResponse({'status': 'error', 'error': 'Invalid request method'})


@login_required(login_url='login')
@role_required(1)
@csrf_exempt
def create_invoice(request):
    if request.method == 'POST':
        data = request.POST
        factuurnummer = data.get('factuurnummer')
        factuurdatum = data.get('factuurdatum')

        selected_event_ids = []
        selected_event_totals = []

        i = 0
        while True:
            event_id = data.get(f'selected_events[{i}][id]')
            totaalbedragWerk = data.get(f'selected_events[{i}][totaalbedragWerk]')
            if not event_id:
                break
            selected_event_ids.append(event_id)
            selected_event_totals.append(totaalbedragWerk)
            i += 1

        if not factuurnummer or not factuurdatum or not selected_event_ids:
            sweetify.error(request, 'Error', text='Vul alstublieft alle velden in en selecteer minstens één event.')
            return JsonResponse({'status': 'error', 'message': 'Missing required fields or no events selected'})

        assistent = request.user.assistent

        try:
            invoice = InvoiceOverview.objects.create(
                invoice_number=factuurnummer,
                invoice_date=factuurdatum,
                invoice_created_by=assistent,
                invoice_amount=round(sum(float(total) for total in selected_event_totals), 2),
                invoice_btw=round(sum(float(total) for total in selected_event_totals) * 0.21, 2),
            )

            events = []
            totaalbedragFactuur = 0.00

            for event_id, total in zip(selected_event_ids, selected_event_totals):
                event = Event.objects.get(id=event_id)
                InvoiceDetail.objects.create(
                    invoice_event=event,
                    invoice_subtotal=float(total),
                    invoice_id=invoice
                )
                event.invoiced = True
                event.save()
                id = event.id
                start_time = event.start_time
                end_time = event.end_time
                aanwezige_tijd = end_time - start_time
                pauzeduur = timedelta(minutes=event.pauzeduur)
                gewerkte_uren = (end_time - start_time - pauzeduur).total_seconds() / 3600
                gewerkte_uren_modal = end_time - start_time - pauzeduur
                gewerkte_uren = round(gewerkte_uren, 4)
                assistent = event.assistent
                apotheek = event.apotheek
                try:
                    link = LinkBetweenAssistentAndApotheek.objects.get(assistent=assistent, apotheek=apotheek)
                    uurtariefAssistent = float(link.uurtariefAssistent)
                    afstandInKilometers = link.afstandInKilometers
                    uurtariefApotheek = float(link.uurtariefApotheek)
                    kilometervergoeding = link.kilometervergoeding
                    bedragFietsvergoeding = 0.00
                    if kilometervergoeding:
                        bedragFietsvergoeding = round(afstandInKilometers * 0.43, 2)
                    totaalbedragZonderFietsvergoeding = round(gewerkte_uren * uurtariefAssistent, 2)
                    totaalbedragWerk = round(round(gewerkte_uren * uurtariefAssistent, 2) + bedragFietsvergoeding, 2)
                    totaalbedragFactuur += totaalbedragWerk
                except:
                    link = ""
                    uurtariefAssistent = 0
                    uurtariefApotheek = 0
                    kilometervergoeding = False
                    afstandInKilometers = 0
                    totaalbedragWerk = 0
                    bedragFietsvergoeding = 0.00
                    totaalbedragZonderFietsvergoeding = 0.00

                item_to_add = {
                    'id': id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'pauzeduur': pauzeduur,
                    'assistent': assistent,
                    'apotheek': apotheek,
                    'link': link,
                    'uurtariefAssistent': uurtariefAssistent,
                    'uurtariefApotheek': uurtariefApotheek,
                    'afstandinKilometers': afstandInKilometers,
                    'kilometervergoeding': kilometervergoeding,
                    'totaalbedragWerk': totaalbedragWerk,
                    'bedragFietsvergoeding': bedragFietsvergoeding,
                    'aanwezige_tijd': aanwezige_tijd,
                    'gewerkte_tijd': gewerkte_uren_modal,
                    'totaalbedrag_zonder_fietsvergoeding': totaalbedragZonderFietsvergoeding
                }
                events.append(item_to_add)

            totaalbedragFactuur = round(totaalbedragFactuur, 2)
            btw = round(totaalbedragFactuur * 0.21, 2)
            totaalbedragFactuurMetBtw = round(totaalbedragFactuur + btw, 2)
            # Ensure invoice_date is a datetime object (convert if necessary)
            if isinstance(invoice.invoice_date, str):
                invoice_date = datetime.strptime(invoice.invoice_date, '%Y-%m-%d')  # Adjust format if needed
            else:
                invoice_date = invoice.invoice_date

            # Format the date to 'dd/mm/yyyy'
            formatted_invoice_date = invoice_date.strftime('%d/%m/%Y')
            items_needed_for_pdf_creation = {
                'events': events,
                'totaalbedragFactuur': totaalbedragFactuur,
                'btw': btw,
                'totaalbedragFactuurMetBtw': totaalbedragFactuurMetBtw,
                'assistent': request.user.assistent,
                'apotheek': 0,
                'invoice': invoice,
                'invoice_date': formatted_invoice_date
            }
            pdf_content = create_pdf(items_needed_for_pdf_creation, 'invoice/invoice_assistent.html')
            if not pdf_content:
                sweetify.error(request, 'Error', text='Fout bij het genereren van de PDF.')
                return JsonResponse({'status': 'error', 'message': 'Error generating PDF'})

            # Save the PDF to the model
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f'invoice_{timestamp}_{invoice.invoice_number}.pdf'
            invoice.invoice_pdf.save(pdf_filename, ContentFile(pdf_content))

            # Provide download link in the response
            download_url = request.build_absolute_uri(invoice.invoice_pdf.url)
            return JsonResponse({'status': 'success', 'pdf_url': download_url, 'download_url': download_url})

        except IntegrityError:
            return JsonResponse(
                {'status': 'error', 'message': 'Factuurnummer bestaat al voor deze assistent. Kies een ander nummer.'})

        except Exception as e:
            sweetify.error(request, 'Error', text=str(e))
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def create_pdf(items, path):
    template_path = path  # Path to your HTML template
    context = {
        'items': items
    }
    response = BytesIO()  # Create an in-memory file object to store the PDF
    template = get_template(template_path)  # Load the HTML template
    html = template.render(context)  # Render the template with context
    pisa_status = pisa.CreatePDF(html, dest=response)  # Convert HTML to PDF
    if pisa_status.err:
        return None  # Return None if there was an error
    return response.getvalue()  # Return the PDF content


@role_required(3)
def overview_facturen_assistent_admin(request, user_id):
    gebruiker = get_object_or_404(User, id=user_id)
    assistent = get_object_or_404(Assistent, user=gebruiker)
    invoices = InvoiceOverview.objects.filter(invoice_created_by=assistent)
    assistent_id = assistent.id

    context = {
        'user_id': user_id,
        'apotheek_id': 0,
        'gebruiker': gebruiker,
        'invoices': invoices,
        'assistent_id': assistent_id
    }

    return render(request, 'invoice/admin/overview_facturen_assistent.html', context)


@role_required(3)
def toggle_invoice_status_factuur_assistent(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        invoice_id = data.get('invoice_id')
        invoice = get_object_or_404(InvoiceOverview, id=invoice_id)
        invoice_detail = InvoiceDetail.objects.filter(invoice_id=invoice)

        if invoice.invoice_paid:
            # If already paid, mark as unpaid and remove the paid timestamp
            invoice.invoice_paid = False
            invoice.invoice_paid_at = None
            invoice.invoice_paid_by = None
            for detail in invoice_detail:
                event = get_object_or_404(Event, id=detail.invoice_event.id)
                event.paid_by_apotheek = False
                event.save()
        else:
            # If unpaid, mark as paid and set the current timestamp
            invoice.invoice_paid = True
            invoice.invoice_paid_at = timezone.now()
            invoice.invoice_paid_by = request.user
            for detail in invoice_detail:
                event = get_object_or_404(Event, id=detail.invoice_event.id)
                event.paid_by_apotheek = False
                event.save()

        invoice.save()

        return JsonResponse({
            'status': invoice.invoice_paid,
            'paid_at': invoice.invoice_paid_at.strftime("%d/%m/%Y %H:%M:%S") if invoice.invoice_paid_at else None
        })


@role_required(3)
def create_invoice_apotheek_admin(request):
    if request.method == 'POST':
        data = request.POST
        factuurnummer = data.get('factuurnummer')
        factuurdatum = data.get('factuurdatum')

        selected_event_ids = []
        selected_event_totals = []

        i = 0
        while True:
            event_id = data.get(f'selected_events[{i}][id]')
            totaalbedragWerk = data.get(f'selected_events[{i}][totaalbedragWerk]')
            if not event_id:
                break
            selected_event_ids.append(event_id)
            selected_event_totals.append(totaalbedragWerk)
            i += 1

        if not factuurnummer or not factuurdatum or not selected_event_ids:
            sweetify.error(request, 'Error', text='Vul alstublieft alle velden in en selecteer minstens één event.')
            return JsonResponse({'status': 'error', 'message': 'Missing required fields or no events selected'})

        try:
            apotheek = 0
            for event_id, total in zip(selected_event_ids, selected_event_totals):
                event = Event.objects.get(id=event_id)
                apotheek = event.apotheek
                break

            invoice = InvoiceApotheekOverview.objects.create(
                invoice_number=factuurnummer,
                invoice_date=factuurdatum,
                invoice_created_by=request.user,
                invoice_amount=round(sum(float(total) for total in selected_event_totals), 2),
                invoice_btw=round(sum(float(total) for total in selected_event_totals) * 0.21, 2),
                invoice_apotheek=apotheek
            )

            events = []
            totaalbedragFactuur = 0.00

            for event_id, total in zip(selected_event_ids, selected_event_totals):
                event = Event.objects.get(id=event_id)
                InvoiceApotheekDetail.objects.create(
                    invoice_event=event,
                    invoice_subtotal=float(total),
                    invoice_id=invoice
                )
                event.invoiced_to_apotheek = True
                event.save()
                id = event.id
                start_time = event.start_time
                end_time = event.end_time
                aanwezige_tijd = end_time - start_time
                pauzeduur = timedelta(minutes=event.pauzeduur)
                gewerkte_uren = (end_time - start_time - pauzeduur).total_seconds() / 3600
                gewerkte_uren_modal = end_time - start_time - pauzeduur
                gewerkte_uren = round(gewerkte_uren, 4)
                assistent = event.assistent
                apotheek = event.apotheek
                try:
                    link = LinkBetweenAssistentAndApotheek.objects.get(assistent=assistent, apotheek=apotheek)
                    uurtariefAssistent = float(link.uurtariefAssistent)
                    afstandInKilometers = link.afstandInKilometers
                    uurtariefApotheek = float(link.uurtariefApotheek)
                    kilometervergoeding = link.kilometervergoeding
                    bedragFietsvergoeding = 0.00
                    if kilometervergoeding:
                        bedragFietsvergoeding = round(afstandInKilometers * 0.43, 2)
                    totaalbedragZonderFietsvergoeding = round(gewerkte_uren * uurtariefApotheek, 2)
                    totaalbedragWerk = round(round(gewerkte_uren * uurtariefApotheek, 2) + bedragFietsvergoeding, 2)
                    totaalbedragFactuur += totaalbedragWerk
                except:
                    link = ""
                    uurtariefAssistent = 0
                    uurtariefApotheek = 0
                    kilometervergoeding = False
                    afstandInKilometers = 0
                    totaalbedragWerk = 0
                    bedragFietsvergoeding = 0.00
                    totaalbedragZonderFietsvergoeding = 0.00

                item_to_add = {
                    'id': id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'pauzeduur': pauzeduur,
                    'assistent': assistent,
                    'apotheek': apotheek,
                    'link': link,
                    'uurtariefAssistent': uurtariefAssistent,
                    'uurtariefApotheek': uurtariefApotheek,
                    'afstandinKilometers': afstandInKilometers,
                    'kilometervergoeding': kilometervergoeding,
                    'totaalbedragWerk': totaalbedragWerk,
                    'bedragFietsvergoeding': bedragFietsvergoeding,
                    'aanwezige_tijd': aanwezige_tijd,
                    'gewerkte_tijd': gewerkte_uren_modal,
                    'totaalbedrag_zonder_fietsvergoeding': totaalbedragZonderFietsvergoeding
                }
                events.append(item_to_add)

            totaalbedragFactuur = round(totaalbedragFactuur, 2)
            btw = round(totaalbedragFactuur * 0.21, 2)
            totaalbedragFactuurMetBtw = round(totaalbedragFactuur + btw, 2)
            # Ensure invoice_date is a datetime object (convert if necessary)
            if isinstance(invoice.invoice_date, str):
                invoice_date = datetime.strptime(invoice.invoice_date, '%Y-%m-%d')  # Adjust format if needed
            else:
                invoice_date = invoice.invoice_date

            # Format the date to 'dd/mm/yyyy'
            formatted_invoice_date = invoice_date.strftime('%d/%m/%Y')
            items_needed_for_pdf_creation = {
                'events': events,
                'totaalbedragFactuur': totaalbedragFactuur,
                'btw': btw,
                'totaalbedragFactuurMetBtw': totaalbedragFactuurMetBtw,
                'apotheek': apotheek,
                'assistent': 0,
                'invoice': invoice,
                'invoice_date': formatted_invoice_date
            }
            pdf_content = create_pdf(items_needed_for_pdf_creation, 'invoice/invoice_apotheek.html')
            if not pdf_content:
                sweetify.error(request, 'Error', text='Fout bij het genereren van de PDF.')
                return JsonResponse({'status': 'error', 'message': 'Error generating PDF'})

            # Save the PDF to the model
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f'invoice_{timestamp}_{invoice.invoice_number}.pdf'
            invoice.invoice_pdf.save(pdf_filename, ContentFile(pdf_content))

            # Provide download link in the response
            download_url = request.build_absolute_uri(invoice.invoice_pdf.url)
            return JsonResponse({'status': 'success', 'pdf_url': download_url, 'download_url': download_url})
        except IntegrityError:
            return JsonResponse(
                {'status': 'error', 'message': 'Factuurnummer bestaat al. Kies een ander nummer.'})

        except Exception as e:
            sweetify.error(request, 'Error', text=str(e))
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@role_required(3)
def overview_facturen_apotheek_admin(request, user_id):
    gebruiker = get_object_or_404(User, id=user_id)
    apotheek = get_object_or_404(Apotheek, user=gebruiker)
    invoices = InvoiceApotheekOverview.objects.filter(invoice_apotheek=apotheek)
    apotheek_id = apotheek.id

    context = {
        'user_id': user_id,
        'apotheek_id': 0,
        'gebruiker': gebruiker,
        'invoices': invoices,
        'apotheek_id': apotheek_id
    }
    return render(request, 'invoice/admin/overview_facturen_apotheek.html', context)


@role_required(3)
def toggle_invoice_status_factuur_apotheek(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        invoice_id = data.get('invoice_id')
        # Fetch the invoice overview object
        invoice = get_object_or_404(InvoiceApotheekOverview, id=invoice_id)

        # Fetch all related invoice details for the invoice
        invoice_details = InvoiceApotheekDetail.objects.filter(invoice_id=invoice)

        if invoice.invoice_paid:
            # If already paid, mark as unpaid and remove the paid timestamp
            invoice.invoice_paid = False
            invoice.invoice_paid_at = None
            invoice.invoice_paid_by = None
            for detail in invoice_details:
                event = detail.invoice_event
                event.paid_by_apotheek = False
                event.save()
        else:
            # If unpaid, mark as paid and set the current timestamp
            invoice.invoice_paid = True
            invoice.invoice_paid_at = timezone.now()
            invoice.invoice_paid_by = request.user
            for detail in invoice_details:
                event = detail.invoice_event
                event.paid_by_apotheek = True
                event.save()

        invoice.save()

        return JsonResponse({
            'status': invoice.invoice_paid,
            'paid_at': invoice.invoice_paid_at.strftime("%d/%m/%Y %H:%M:%S") if invoice.invoice_paid_at else None
        })


@require_POST
@role_required(3)
def create_link_between_assistent_and_apotheek(request):
    link_id = request.POST.get('link_id')
    assistent_id = request.POST.get('assistent')
    apotheek_id = request.POST.get('apotheek')
    uurtariefAssistent = request.POST.get('uurtariefAssistent')
    uurtariefApotheek = request.POST.get('uurtariefApotheek')
    kilometervergoeding = request.POST.get('kilometervergoeding') == 'on'
    afstandInKilometers = request.POST.get('afstandInKilometers')

    assistent = get_object_or_404(Assistent, pk=assistent_id)
    apotheek = get_object_or_404(Apotheek, pk=apotheek_id)

    if link_id:
        # Update existing link
        link = get_object_or_404(LinkBetweenAssistentAndApotheek, pk=link_id)
        link.uurtariefAssistent = uurtariefAssistent
        link.uurtariefApotheek = uurtariefApotheek
        link.kilometervergoeding = kilometervergoeding
        link.afstandInKilometers = afstandInKilometers
    else:
        # Create new link
        link, created = LinkBetweenAssistentAndApotheek.objects.get_or_create(
            assistent=assistent,
            apotheek=apotheek,
            defaults={
                'uurtariefAssistent': uurtariefAssistent,
                'uurtariefApotheek': uurtariefApotheek,
                'kilometervergoeding': kilometervergoeding,
                'afstandInKilometers': afstandInKilometers,
            }
        )
        if not created:
            # If the link already exists, update the fields
            link.uurtariefAssistent = uurtariefAssistent
            link.uurtariefApotheek = uurtariefApotheek
            link.kilometervergoeding = kilometervergoeding
            link.afstandInKilometers = afstandInKilometers

    link.save()

    return JsonResponse({'success': True})


@role_required(3)
def overview_all_invoices_assistenten_admin(request):
    # Huidige datum en tijd
    today = now().date()

    # Begin en einde van de vorige maand
    first_day_of_month = today.replace(day=1)
    last_month_end = first_day_of_month - timedelta(days=1)
    first_day_of_last_month = last_month_end.replace(day=1)

    # Facturen van de afgelopen maand
    last_month_invoices = InvoiceOverview.objects.filter(invoice_date__range=[first_day_of_last_month, last_month_end])

    # Omzet afgelopen maand (som van invoice_amount + invoice_btw)
    omzet_last_month = last_month_invoices.aggregate(
        total=Sum(F('invoice_amount') + F('invoice_btw'))
    )

    # Aantal facturen afgelopen maand
    invoice_count_last_month = last_month_invoices.count()

    # Aantal unieke personen die een factuur maakten
    unique_person_count = last_month_invoices.values('invoice_created_by').distinct().count()

    # Totale bedrag dat nog niet betaald is (som van invoice_amount + invoice_btw)
    unpaid_invoices = InvoiceOverview.objects.filter(invoice_paid=False)
    unpaid_amount = unpaid_invoices.aggregate(
        total_unpaid=Sum(F('invoice_amount') + F('invoice_btw'))
    )

    # Afronden van de bedragen op 2 decimalen
    omzet_last_month_value = omzet_last_month['total'] if omzet_last_month['total'] is not None else 0
    omzet_last_month_rounded = round(omzet_last_month_value, 2)

    unpaid_amount_value = unpaid_amount['total_unpaid'] if unpaid_amount['total_unpaid'] is not None else 0
    unpaid_amount_rounded = round(unpaid_amount_value, 2)

    # Limiet van het aantal records op basis van de gebruiker selectie (standaard 10)
    limit = request.GET.get('limit', 10)

    # Alle assistentenfacturen (voor weergave in de tabel)
    all_assistenten_invoices = InvoiceOverview.objects.all().order_by('-invoice_date', 'invoice_created_by__user__last_name')

    # Paginator
    paginator = Paginator(all_assistenten_invoices, limit)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'omzet_last_month': omzet_last_month_rounded,
        'invoice_count_last_month': invoice_count_last_month,
        'unique_person_count': unique_person_count,
        'unpaid_amount': unpaid_amount_rounded
    }

    return render(request, 'invoice/admin/overview_invoices_assistenten.html', context)


@role_required(3)
def overview_all_invoices_apotheken_admin(request):
    # Huidige datum en tijd
    today = now().date()

    # Begin en einde van de vorige maand
    first_day_of_month = today.replace(day=1)
    last_month_end = first_day_of_month - timedelta(days=1)
    first_day_of_last_month = last_month_end.replace(day=1)

    # Facturen van de afgelopen maand
    last_month_invoices = InvoiceApotheekOverview.objects.filter(invoice_date__range=[first_day_of_last_month, last_month_end])
    # Aantal facturen afgelopen maand
    invoice_count_last_month = last_month_invoices.count()
    # Omzet afgelopen maand (som van invoice_amount + invoice_btw)
    omzet_last_month = last_month_invoices.aggregate(
        total=Sum(F('invoice_amount') + F('invoice_btw'))
    )

    # Afronden van de bedragen op 2 decimalen
    omzet_last_month_value = omzet_last_month['total'] if omzet_last_month['total'] is not None else 0
    omzet_last_month_rounded = round(omzet_last_month_value, 2)

    # Aantal unieke personen die een factuur maakten
    unique_person_count = last_month_invoices.values('invoice_apotheek').distinct().count()

    # Totale bedrag dat nog niet betaald is (som van invoice_amount + invoice_btw)
    unpaid_invoices = InvoiceApotheekOverview.objects.filter(invoice_paid=False)
    unpaid_amount = unpaid_invoices.aggregate(
        total_unpaid=Sum(F('invoice_amount') + F('invoice_btw'))
    )
    unpaid_amount_value = unpaid_amount['total_unpaid'] if unpaid_amount['total_unpaid'] is not None else 0
    unpaid_amount_rounded = round(unpaid_amount_value, 2)

    # Limiet van het aantal records op basis van de gebruiker selectie (standaard 10)
    limit = request.GET.get('limit', 10)

    # Alle facturen, geordend op factuurdatum en achternaam
    all_apotheken_invoices = InvoiceApotheekOverview.objects.all().order_by('-invoice_date', 'invoice_apotheek__user__last_name')

    # Paginator
    paginator = Paginator(all_apotheken_invoices, limit)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'omzet_last_month': omzet_last_month_rounded,
        'invoice_count_last_month': invoice_count_last_month,
        'unique_person_count': unique_person_count,
        'unpaid_amount': unpaid_amount_rounded,
        'all_apotheken_invoices': all_apotheken_invoices,
    }
    return render(request, 'invoice/admin/overview_invoices_apotheken.html', context)


@role_required(3)
def get_filtered_invoices(request):
    status = request.GET.get('status')

    if status == 'all':
        invoices = InvoiceOverview.objects.all()
    else:
        paid_status = status == 'true'
        invoices = InvoiceOverview.objects.filter(invoice_paid=paid_status)

    data = list(invoices.values(
        'id',
        'invoice_number',
        'invoice_pdf',
        'invoice_amount',
        'invoice_btw',
        'invoice_date',
        'invoice_created_by__user__first_name',
        'invoice_created_by__user__last_name',
        'invoice_created_by__assistent_naamBedrijf',
        'invoice_paid'
    ))

    for invoice in data:
        invoice[
            'invoice_created_by_name'] = f"{invoice.pop('invoice_created_by__user__first_name')} {invoice.pop('invoice_created_by__user__last_name')}"
        invoice['invoice_created_by_company'] = invoice.pop('invoice_created_by__assistent_naamBedrijf')
        invoice['invoice_pdf_url'] = invoice.pop('invoice_pdf')
        invoice['invoice_date'] = invoice.pop('invoice_date').strftime("%d/%m/%Y")
        invoice['invoice_paid'] = 'Betaald' if invoice['invoice_paid'] else 'Te Betalen'

    return JsonResponse(data, safe=False)


@role_required(3)
def get_filtered_invoices_to_apotheek(request):
    status = request.GET.get('status')
    limit = request.GET.get('limit', 10)  # Default is 10 items per pagina

    if status == 'all':
        invoices = InvoiceApotheekOverview.objects.all()
    else:
        paid_status = status == 'true'
        invoices = InvoiceApotheekOverview.objects.filter(invoice_paid=paid_status)

    paginator = Paginator(invoices, limit)  # Paginering toepassen
    page_number = request.GET.get('page', 1)  # Standaard pagina 1
    page_obj = paginator.get_page(page_number)

    data = list(page_obj.object_list.values(
        'id',
        'invoice_number',
        'invoice_pdf',
        'invoice_amount',
        'invoice_btw',
        'invoice_date',
        'invoice_apotheek__user__first_name',
        'invoice_apotheek__user__last_name',
        'invoice_apotheek__apotheek_naamBedrijf',
        'invoice_paid'
    ))

    for invoice in data:
        invoice[
            'invoice_created_by_name'] = f"{invoice.pop('invoice_apotheek__user__first_name')} {invoice.pop('invoice_apotheek__user__last_name')}"
        invoice['invoice_created_by_company'] = invoice.pop('invoice_apotheek__apotheek_naamBedrijf')
        invoice['invoice_pdf_url'] = invoice.pop('invoice_pdf')
        invoice['invoice_date'] = invoice.pop('invoice_date').strftime("%d/%m/%Y")
        invoice['invoice_paid'] = 'Betaald' if invoice['invoice_paid'] else 'Te Betalen'

    response_data = {
        'invoices': data,
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    }

    return JsonResponse(response_data)