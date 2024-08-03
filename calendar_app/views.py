import json

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.utils.timezone import localtime
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from accounts.models import User
from .models import Assistent, Apotheek, Event


def calendar_view(request):
    return render(request, 'calendar/calendar.html')


def events_json(request):
    try:
        user = request.user
        events = Event.objects.all()

        if user.role == User.ASSISTENT:
            # For Assistents, filter events by the assistent
            assistent = Assistent.objects.get(user=user)
            events = Event.objects.filter(assistent=assistent)
        elif user.role == User.ADMIN:
            pass
            # Admins can see all events
        else:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        events_list = [
            {
                'id': event.id,
                'start': localtime(event.start_time).isoformat(),
                'end': localtime(event.end_time).isoformat(),
                'category': dict(Event.CATEGORY_CHOICES).get(event.category,
                                                             'Unknown') if user.role == User.ASSISTENT else None,
                'assistent_name': event.assistent.user.first_name + ' ' + event.assistent.user.last_name if user.role == User.ADMIN else None,
                'apotheek': event.apotheek.id if event.apotheek else None,
                'apotheek_naam': event.apotheek.apotheek_naamBedrijf if event.apotheek else None,
                'created_by': event.created_by.id if event.created_by else None,
                'status': event.status,
                'created_date': localtime(event.created_date).isoformat() if event.created_date else None,
                'modified_date': localtime(event.modified_date).isoformat() if event.modified_date else None,
                'status_last_changed_date': localtime(
                    event.status_last_changed_date).isoformat() if event.status_last_changed_date else None,
                'user_role': request.user.role
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


def fetch_assistents(request):
    if request.method == 'GET':
        assistents = Assistent.objects.all()
        assistents_list = [
            {
                'id': assistent.id,
                'name': f'{assistent.user.first_name} {assistent.user.last_name}'
            }
            for assistent in assistents
        ]
        return JsonResponse(assistents_list, safe=False)


def fetch_apotheken(request):
    if request.method == 'GET':
        apotheken = Apotheek.objects.all()
        apotheken_list = [
            {
                'id': apotheek.id,
                'name': apotheek.apotheek_naamBedrijf
            }
            for apotheek in apotheken
        ]
        return JsonResponse(apotheken_list, safe=False)


@csrf_exempt
def add_event(request):
    if request.method == 'POST':
        try:
            # Load JSON data
            data = json.loads(request.body)

            # Validate input data
            required_fields = ['date', 'startTime', 'endTime', 'assistent', 'apotheek']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

            # Format and validate date and time
            try:
                start_time = parse_datetime(f"{data['date']}T{data['startTime']}")
                end_time = parse_datetime(f"{data['date']}T{data['endTime']}")
                if not start_time or not end_time:
                    raise ValidationError("Invalid date or time format")
            except (ValueError, ValidationError) as e:
                return JsonResponse({'error': str(e)}, status=400)

            # Check if assistent and apotheek exist
            try:
                assistent = Assistent.objects.get(id=data['assistent'])
                apotheek = Apotheek.objects.get(id=data['apotheek'])
            except Assistent.DoesNotExist:
                return JsonResponse({'error': 'Assistent not found'}, status=404)
            except Apotheek.DoesNotExist:
                return JsonResponse({'error': 'Apotheek not found'}, status=404)

            # Create and save the event
            event = Event(
                start_time=start_time,
                end_time=end_time,
                assistent=assistent,
                apotheek=apotheek,
                category='werk',  # Default category or adjust as needed
                created_by=request.user,
                status='noaction'
            )
            event.save()

            # Return success response
            return JsonResponse({'status': 'success', 'event_id': event.id})

        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON data', 'details': str(e)}, status=400)
        except Exception as e:
            # Log unexpected exceptions
            print("Unexpected error:", str(e))
            return JsonResponse({'error': 'Internal server error', 'details': str(e)}, status=500)

    # Handle non-POST requests
    return JsonResponse({'error': 'Invalid request method'}, status=405)