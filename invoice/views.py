import json

import pytz
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from accounts.decorators import role_required
from accounts.models import Assistent, User, Apotheek
from calendar_app.models import Event
from invoice.forms import LinkBetweenAssistentAndApotheekForm
from invoice.models import LinkBetweenAssistentAndApotheek


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

    # Determine role and get the appropriate instance
    if gebruiker.role == 1:
        assistent = get_object_or_404(Assistent, user=gebruiker)
        assistent_id = assistent.id
        links = LinkBetweenAssistentAndApotheek.objects.filter(assistent=assistent)
    elif gebruiker.role == 2:
        apotheek = get_object_or_404(Apotheek, user=gebruiker)
        apotheek_id = apotheek.id
        links = LinkBetweenAssistentAndApotheek.objects.filter(apotheek=apotheek)

    # Prepare the form for the modal
    if request.method == 'POST':
        form = LinkBetweenAssistentAndApotheekForm(request.POST)
        if form.is_valid():
            form.save()
            # Optionally, you can redirect to the same page or another page after successful submission
            return redirect('overview_link_assistent_apotheek_admin', user_id=user_id)
        # If the form is not valid, the errors will be passed to the template as part of the form
    else:
        form = LinkBetweenAssistentAndApotheekForm()

    # Pass the context to the template
    context = {
        'user_id': user_id,
        'gebruiker': gebruiker,
        'assistent_id': assistent_id,
        'apotheek_id': apotheek_id,
        'links': links,
        'form': form,
        'assistent': assistent,  # Pass the Assistent object
        'apotheek': apotheek,  # Pass the Apotheek object
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
        # Log the raw request body
        print('Raw request body:', request.body.decode('utf-8'))

        try:
            data = json.loads(request.body)  # Parse the JSON data
            status_apotheek = data.get('status_apotheek')

            # Log the extracted data
            print('Extracted Status:', status_apotheek)

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
        # Log the raw request body
        print('Raw request body:', request.body.decode('utf-8'))

        try:
            data = json.loads(request.body)  # Parse the JSON data
            status = data.get('status')

            # Log the extracted data
            print('Extracted Status:', status)

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
    nog_te_factureren_events = Event.objects.filter(assistent=assistent, invoiced=False, status='Accepted',
                                                    status_apotheek='Accepted')
    context = {
        'te_bekijken_events_door_assistent': te_bekijken_events_door_assistent,
        'nog_te_factureren_events': nog_te_factureren_events
    }
    return render(request, 'invoice/overview_events_assistent.html', context)


@role_required(3)
def delete_link(request, user_id, link_id):
    link = get_object_or_404(LinkBetweenAssistentAndApotheek, id=link_id)

    if request.method == 'POST':
        # Ensure that the current user has permission to delete the link
        link.delete()
        messages.success(request, 'De link is succesvol verwijderd.')

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
    nog_te_factureren_dagen = None
    gefactureerde_dagen_aan_apotheek = None
    betaalde_dagen_door_apotheek = None

    # Determine role and get the appropriate instance
    if gebruiker.role == 1:
        assistent = get_object_or_404(Assistent, user=gebruiker)
        assistent_id = assistent.id
        events_status_no_action = Event.objects.filter(assistent=assistent, status='noaction').order_by('start_time')
        gewerkte_dagen_te_accepteren_door_apotheek = Event.objects.filter(assistent=assistent,
                                                                          status='Accepted').exclude(
            status_apotheek='Accepted').order_by('start_time')
        nog_te_factureren_dagen_aan_apotheek = Event.objects.filter(assistent=assistent, status='Accepted',
                                                                    status_apotheek='Accepted', invoiced=True,
                                                                    invoiced_to_apotheek=False).order_by('start_time')
        nog_te_factureren_dagen = Event.objects.filter(assistent=assistent, status='Accepted',
                                                       status_apotheek='Accepted', invoiced=False).order_by(
            'start_time')
        gefactureerde_dagen_aan_apotheek = Event.objects.filter(assistent=assistent, status='Accepted',
                                                                status_apotheek='Accepted', invoiced=True,
                                                                invoiced_to_apotheek=True,
                                                                paid_by_apotheek=False).order_by('start_time')

        betaalde_dagen_door_apotheek = Event.objects.filter(assistent=assistent, status='Accepted',
                                                            status_apotheek='Accepted', invoiced=True,
                                                            invoiced_to_apotheek=True, paid_by_apotheek=True).order_by(
            'start_time')

    elif gebruiker.role == 2:
        apotheek = get_object_or_404(Apotheek, user=gebruiker)
        apotheek_id = apotheek.id
        events_status_no_action = Event.objects.filter(apotheek=apotheek, status='noaction').order_by('start_time')
        nog_te_factureren_dagen_aan_apotheek = Event.objects.filter(apotheek=apotheek, status='Accepted',
                                                                    status_apotheek='Accepted', invoiced=True,
                                                                    invoiced_to_apotheek=False).order_by('start_time')
        gewerkte_dagen_te_accepteren_door_apotheek = Event.objects.filter(apotheek=apotheek, status='Accepted').exclude(
            status_apotheek='Accepted').order_by('start_time')
        nog_te_factureren_dagen = Event.objects.filter(apotheek=apotheek, status='Accepted',
                                                       status_apotheek='Accepted', invoiced=False).order_by(
            'start_time')
        gefactureerde_dagen_aan_apotheek = Event.objects.filter(apotheek=apotheek, status='Accepted',
                                                                status_apotheek='Accepted', invoiced=True,
                                                                invoiced_to_apotheek=True,
                                                                paid_by_apotheek=True).order_by('start_time')

        betaalde_dagen_door_apotheek = Event.objects.filter(apotheek=apotheek, status='Accepted',
                                                            status_apotheek='Accepted', invoiced=True,
                                                            invoiced_to_apotheek=True, paid_by_apotheek=True).order_by(
            'start_time')

    context = {
        'user_id': user_id,
        'gebruiker': gebruiker,
        'assistent_id': assistent_id,
        'apotheek_id': apotheek_id,
        'assistent': assistent,  # Pass the Assistent object
        'apotheek': apotheek,  # Pass the Apotheek object
        'events_status_no_action': events_status_no_action,
        'gewerkte_dagen_te_accepteren_door_apotheek': gewerkte_dagen_te_accepteren_door_apotheek,
        'nog_te_factureren_dagen_aan_apotheek': nog_te_factureren_dagen_aan_apotheek,
        'nog_te_factureren_dagen': nog_te_factureren_dagen,
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

    paginator_nog_te_factureren_door_assistent = Paginator(nog_te_factureren_door_assistent, 5)
    page_number_nog_te_factureren_door_assistent = request.GET.get('page_nog_te_factureren_door_assistent')
    paginator_nog_te_factureren_door_assistent_obj = paginator_nog_te_factureren_door_assistent.get_page(
        page_number_nog_te_factureren_door_assistent)

    paginator_nog_te_factureren_aan_apotheek = Paginator(nog_te_factureren_aan_apotheek, 5)
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
            event.pauzeDuur = data.get('pauzeDuur')
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
