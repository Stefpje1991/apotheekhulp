from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from accounts.decorators import role_required
from accounts.models import Assistent, User, Apotheek
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
