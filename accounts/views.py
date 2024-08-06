from django.contrib import messages, auth
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .decorators import admin_required, role_required

from .forms import UserCreationForm, AssistentForm, ApotheekForm, UserEditForm, ChangePasswordForm
from .models import User, Assistent, Apotheek


def login_view(request):
    if request.method == "POST":
        email = request.POST['email-username']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Succesvol aangemeld')
            return redirect('home')  # Redirect to a success page.
        else:
            # Return an 'invalid login' error message.
            messages.error(request, 'Ongeldige gebruikersnaam of wachtwoord')
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "Succesvol afgemeld")
    return redirect('home')


@role_required(3)
def register(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        assistent_form = ""
        apotheek_form = ""
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            role = user_form.cleaned_data.get('role')
            user.username = user.email
            user.save()
            if role == User.ASSISTENT:
                assistent_form = AssistentForm(request.POST)
                if assistent_form.is_valid():
                    assistent = assistent_form.save(commit=False)
                    assistent.user = user
                    assistent.save()
            elif role == User.APOTHEEK:
                apotheek_form = ApotheekForm(request.POST)
                if apotheek_form.is_valid():
                    apotheek = apotheek_form.save(commit=False)
                    apotheek.user = user
                    apotheek.save()
            return redirect('home')
    else:
        user_form = UserCreationForm()
        assistent_form = AssistentForm()
        apotheek_form = ApotheekForm()

    return render(request, 'accounts/register.html', {
        'user_form': user_form,
        'assistent_form': assistent_form,
        'apotheek_form': apotheek_form,
    })


@login_required(login_url='login')
def edit_userprofile(request):
    if request.method == 'POST':
        user = request.user
        if 'delete_profile_picture' in request.POST:
            user.profile_picture.delete(save=False)  # Delete the profile picture file
            user.profile_picture = None  # Set the profile picture field to None
            user.save()
            messages.success(request, "Profielfoto is verwijderd")
            return redirect('edit_userprofile')
        else:
            form = UserEditForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Gebruikersprofiel werd aangepast")
                return redirect('edit_userprofile')
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'accounts/userprofile.html', {'form': form})


@login_required(login_url='login')
@role_required(1, 2)
def edit_companyprofile(request):
    user = request.user

    if user.role == 1:
        form_class = AssistentForm
        company_instance = Assistent.objects.get(user=user)  # Replace with correct query
    else:
        form_class = ApotheekForm
        company_instance = Apotheek.objects.get(user=user)  # Replace with correct query

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=company_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Bedrijfsprofiel werd aangepast")
            return redirect('edit_companyprofile')
        else:
            print(form.errors)
    else:
        form = form_class(instance=company_instance)

    return render(request, 'accounts/companyprofile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['password']
            user = request.user
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Important, to keep the user logged in
            messages.success(request, 'Je wachtwoord werd succesvol aangepast!')
            return redirect('home')  # Redirect to a success page or profile page
    else:
        form = ChangePasswordForm()

    return render(request, 'accounts/change_password.html', {'form': form})


@login_required(login_url='login')
@role_required(3)
def overview_assistenten(request):
    assistenten = Assistent.objects.all().order_by('user__last_name')
    context = {
        'assistenten': assistenten
    }
    return render(request, 'accounts/overview_assistenten.html', context)


@login_required(login_url='login')
@role_required(3)
def overview_apotheken(request):
    return render(request, 'accounts/overview_apotheken.html')


@login_required(login_url='login')
def edit_assistentprofile(request, assistent_id):
    # Fetch the Assistent object and its associated User
    assistent = get_object_or_404(Assistent, id=assistent_id)
    gebruiker = assistent.user

    if request.method == 'POST':
        # Handle deletion of profile picture
        if 'delete_profile_picture' in request.POST:
            if gebruiker.profile_picture:
                gebruiker.profile_picture.delete(save=False)  # Delete the profile picture file
                gebruiker.profile_picture = None  # Set the profile picture field to None
                gebruiker.save()
                messages.success(request, "Profielfoto is verwijderd")
            return redirect('edit_assistentprofile', assistent_id=assistent_id)

        # Handle form submission for editing user details
        form = UserEditForm(request.POST, request.FILES, instance=gebruiker)
        if form.is_valid():
            form.save()
            messages.success(request, "Gebruikersprofiel werd aangepast")
            return redirect('edit_assistentprofile', assistent_id=assistent_id)
    else:
        print("ELSE")
        form = UserEditForm(instance=gebruiker)
        context = {
            'form': form,
            'assistent_id': assistent_id,
            'gebruiker': gebruiker
        }
        return render(request, 'accounts/userprofile_adminview.html', context=context)
