from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import localtime
from django.views.decorators.csrf import csrf_exempt

from accounts.models import Assistent
from calendar_app.models import Event


def calendar_view(request):
    return render(request, 'calendar/calendar.html')


def events_json(request):
    try:
        assistent = Assistent.objects.get(user=request.user)
        events = Event.objects.filter(assistent=assistent)

        events_list = [
            {
                'id': event.id,
                'start': localtime(event.start_time).isoformat(),
                'end': localtime(event.end_time).isoformat(),
                'category': dict(Event.CATEGORY_CHOICES).get(event.category, 'Unknown'),  # Get the human-readable category name
                'assistent': event.assistent.id if event.assistent else None,
                'apotheek': event.apotheek.id if event.apotheek else None,
                'apotheek_naam': event.apotheek.apotheek_naamBedrijf if event.apotheek else None,
                'created_by': event.created_by.id if event.created_by else None,
                'status': event.status,
                'created_date': localtime(event.created_date).isoformat() if event.created_date else None,
                'modified_date': localtime(event.modified_date).isoformat() if event.modified_date else None,
                'status_last_changed_date': localtime(
                    event.status_last_changed_date).isoformat() if event.status_last_changed_date else None,
            }
            for event in events
        ]
        return JsonResponse(events_list, safe=False)
    except Assistent.DoesNotExist:
        return JsonResponse({'error': 'Assistent not found for the logged-in user'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def update_event_status(request, event_id, action):
    if request.method == 'POST':
        try:
            event = Event.objects.get(id=event_id)
            if action == 'accept':
                event.status = 'Accepted'
            elif action == 'reject':
                event.status = 'Declined'
            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)

            event.save()
            return JsonResponse({'status': event.status})

        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)