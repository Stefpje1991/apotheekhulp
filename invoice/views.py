import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

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
    assistent = ""
    apotheek = ""

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
            return JsonResponse({'success': True})
        else:
            # Collect and format form errors
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
            return JsonResponse({'success': False, 'errors': errors})
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


@role_required(2)
@login_required(login_url='login')
def overview_events_apotheek_and_admin(request):
    user_id = request.user.id
    apotheek = get_object_or_404(Apotheek, user=request.user)
    te_bekijken_events_door_apotheek = Event.objects.filter(apotheek=apotheek, status='Accepted',
                                                            status_apotheek='noaction')
    apotheek_id = apotheek.id
    links = LinkBetweenAssistentAndApotheek.objects.filter(apotheek=apotheek)
    context = {
        'user_id': user_id,
        'events_to_be_reviewed_by_apotheek': te_bekijken_events_door_apotheek,
        'apotheek': apotheek,
        'apotheek_id': apotheek_id,
        'links': links
    }
    return render(request, 'invoice/overview_events_apotheek_and_admin.html', context)


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
            event.save()

            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Event not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
